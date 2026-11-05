#!/usr/bin/env node
/* test_motor.js — regresión del motor de búsqueda de IFAS.
   Uso (raíz del clon, con index.html e idx/):  node test_motor.js [ONYX|N16|TODOS]
   Extrae el motor BM25 de index.html, carga idx/ como lo hace la app y comprueba que cada
   consulta de campo devuelva, dentro del TOP_K, el documento (y opcionalmente la página) esperado.
   Cada caso declara en qué familia se evalúa ('ONYX', 'N16' o 'AMBAS'); los de otra familia se
   saltan y no cuentan como fallo, porque con la familia cambiada la respuesta correcta puede ser
   otro documento. Falla (exit 1) si alguna consulta pierde su resultado. Añade casos cuando
   corrijas un fallo real. */
const fs = require('fs');
const fam = process.argv[2] || 'ONYX';

// ---- casos: [consulta, documento esperado, página (o null), familia en la que se evalúa] ----
// El cuarto campo dice en qué familia tiene sentido juzgar el caso: 'ONYX', 'N16' o 'AMBAS'.
// Un caso de otra familia se salta, no se cuenta como fallo. Casi todos son 'AMBAS': aunque la
// familia seleccionada penalice la otra, no hay documento rival que les gane. Se marcan 'ONYX'
// los casos en los que la respuesta correcta DEPENDE de la familia, porque con N16 seleccionada
// gana —con razón— un documento de la familia N16.
const CASOS = [
  ['para que sirve el jumper j5 en la tarjeta madre nfs2-3030', '52546SP', 33, 'AMBAS'],
  ['jumper j5 cpu2-3030 auxiliary trouble', '52545SP', 40, 'AMBAS'],
  ['tabla h.2 auxiliary trouble 52545sp', '52545SP', 157, 'AMBAS'],
  ['NFS2-3030 software mismatch CPU V22 LCM', 'PPT05', 18, 'AMBAS'],
  ['falla a tierra intermitente en el panel', 'Falla_Tierra', 1, 'AMBAS'],
  ['como actualizar el firmware del nfs2-640', 'Firmware_Upgrade_NFS2-640_-_NFS-320_HQ', 1, 'AMBAS'],
  ['NFS2-3030 firmware version 31 upgrade', 'NFS2-3030_Firmware_Upgrade_a_Version_31', 1, 'AMBAS'],
  ['walk test como activar', 'Walk_Test', 1, 'AMBAS'],
  ['AMPS-24 configurar supervision', 'Como_Configurar_una_Fuente_AMPS_24', 1, 'AMBAS'],
  ['AMPS-24 battery charger 7 to 200 AH', '51907', null, 'AMBAS'],
  ['corriente standby FSP-951', 'DN-60977', null, 'AMBAS'],
  // con N16 gana LS10238-000GE-E (manual ACS-30, familia N16) sobre el datasheet ONYX del FSP-851
  ['FSP-851 current draw standby alarm', 'DN-6935', null, 'ONYX'],
  ['FCO-851 datasheet corriente', 'DN-60689', null, 'AMBAS'],
  ['base sonora B200S corriente', 'I56-3387', null, 'AMBAS'],
  ['NBG-12LX estacion manual direccionable', 'DN-6726', null, 'AMBAS'],
  ['ISO-X aislador de fallas', 'DN-2243', null, 'AMBAS'],
  ['FCM-1-REL modulo de liberacion', 'I56-2992-004', null, 'AMBAS'],
  ['cable NEC 760 FPLR', 'NEC Articulo 760', null, 'AMBAS'],
  // con N16 gana DN-62112 (datasheet del N16, familia N16) sobre el del HS-NCM
  ['HS-NCM datasheet fibra multimodo', 'DN-60454', null, 'ONYX'],
  ['NCA-2 anunciador de red', '52482', null, 'AMBAS'],
  ['FCPS-24S6 standby current 65 mA batteries', '51977', 11, 'AMBAS'],
  ['PSE-10 maximum battery capacity 33 AH', 'LS10227-000NF-E', 9, 'AMBAS'],
  ['ACPS-610 charges 12 to 200 AH batteries', '53018', null, 'AMBAS'],
  ['recuperación de contraseña password agreement', 'Recuperacion de Contraseñas Paneles Notifier', null, 'AMBAS'],
  ['device compatibility document supplement 15378SUP', '15378SUP', null, 'AMBAS'],
  ['SWIFT gateway inalambrico FWSG', 'DN-60820', null, 'AMBAS'],
  ['LCM-320 LEM-320 datasheet lazos', 'DN-6881', null, 'AMBAS'],
  ['SLC wiring manual estilo 4 7', '51253', null, 'AMBAS'],
  ['SLM-318 signaling loop module installation TB1', 'LS10243-000NF-E', null, 'AMBAS'],
  ['PPT08 Convert Node N16 V5.0', 'PPT08', 97, 'AMBAS'],
];

// ---- extraer el motor de index.html ----
const html = fs.readFileSync('index.html', 'utf8');
const js = html.match(/<script>([\s\S]*?)<\/script>/g)[1].slice(8, -9);
let code = js.slice(js.indexOf('const STOP = new Set'), js.indexOf('// ── BUILD API MESSAGES ──'));
const topk = parseInt((js.match(/const TOP_K = (\d+)/) || [0, 10])[1]);
code = `let docIndex=[],bm25=null,indexReady=false,manifest=null;const loadedCats=new Set();let familia='${fam}';const TOP_K=${topk};
const docStatus={style:{}};const localStorage={setItem(){},getItem(){return null}};const document={getElementById(){return {addEventListener(){}}}};
global.fetch=async(u)=>({ok:true,json:async()=>JSON.parse(require('fs').readFileSync(u,'utf8'))});
` + code + `\nmodule.exports={loadIndex,ensureIndexesFor,retrieve};`;
const tmp = require('path').join(require('os').tmpdir(), 'ifas_motor_test.js');
fs.writeFileSync(tmp, code);
const M = require(tmp);

(async () => {
  const t0 = Date.now();
  await M.loadIndex();
  console.log(`índices cargados (${fam}) en ${Date.now() - t0} ms · TOP_K ${topk}`);
  let fallos = 0, corridos = 0, saltados = 0;
  for (const [q, doc, pag, famCaso] of CASOS) {
    // con TODOS no hay penalización de familia, así que todos los casos son evaluables
    if (famCaso && famCaso !== 'AMBAS' && famCaso !== fam && fam !== 'TODOS') {
      saltados++;
      console.log(`· ${q}   (solo ${famCaso})`);
      continue;
    }
    corridos++;
    await M.ensureIndexesFor(q);
    const r = M.retrieve(q, topk);
    const pos = r.findIndex(d => d.doc === doc && (pag == null || d.page === pag));
    const ok = pos >= 0;
    if (!ok) fallos++;
    console.log(`${ok ? '✓' : '✗'} ${q}  →  ${doc}${pag ? ' p.' + pag : ''}` + (ok ? ` (#${pos + 1})` : `   top: ${r.slice(0, 3).map(d => d.doc + ':' + d.page).join(', ')}`));
  }
  console.log(`\n${corridos - fallos}/${corridos} consultas correctas` +
    (saltados ? `  ·  ${saltados} saltadas por familia (de ${CASOS.length} casos)` : ''));
  process.exit(fallos ? 1 : 0);
})();

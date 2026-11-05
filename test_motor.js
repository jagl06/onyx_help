#!/usr/bin/env node
/* test_motor.js — regresión del motor de búsqueda de IFAS.
   Uso (raíz del clon, con index.html e idx/):  node test_motor.js [ONYX|N16|TODOS]
   Extrae el motor BM25 de index.html, carga idx/ como lo hace la app y comprueba que cada
   consulta de campo devuelva, dentro del TOP_K, el documento (y opcionalmente la página) esperado.
   Falla (exit 1) si alguna consulta pierde su resultado. Añade casos cuando corrijas un fallo real. */
const fs = require('fs');
const fam = process.argv[2] || 'ONYX';

// ---- casos: consulta → documento esperado (+ página opcional, familia que debe estar cargada) ----
const CASOS = [
  ['para que sirve el jumper j5 en la tarjeta madre nfs2-3030', '52546SP', 33],
  ['jumper j5 cpu2-3030 auxiliary trouble', '52545SP', 40],
  ['tabla h.2 auxiliary trouble 52545sp', '52545SP', 157],
  ['NFS2-3030 software mismatch CPU V22 LCM', 'PPT05', 18],
  ['falla a tierra intermitente en el panel', 'Falla_Tierra', 1],
  ['como actualizar el firmware del nfs2-640', 'Firmware_Upgrade_NFS2-640_-_NFS-320_HQ', 1],
  ['NFS2-3030 firmware version 31 upgrade', 'NFS2-3030_Firmware_Upgrade_a_Version_31', 1],
  ['walk test como activar', 'Walk_Test', 1],
  ['AMPS-24 configurar supervision', 'Como_Configurar_una_Fuente_AMPS_24', 1],
  ['AMPS-24 battery charger 7 to 200 AH', '51907', null],
  ['corriente standby FSP-951', 'DN-60977', null],
  ['FSP-851 current draw standby alarm', 'DN-6935', null],
  ['FCO-851 datasheet corriente', 'DN-60689', null],
  ['base sonora B200S corriente', 'I56-3387', null],
  ['NBG-12LX estacion manual direccionable', 'DN-6726', null],
  ['ISO-X aislador de fallas', 'DN-2243', null],
  ['FCM-1-REL modulo de liberacion', 'I56-2992-004', null],
  ['cable NEC 760 FPLR', 'NEC Articulo 760', null],
  ['HS-NCM datasheet fibra multimodo', 'DN-60454', null],
  ['NCA-2 anunciador de red', '52482', null],
  ['FCPS-24S6 standby current 65 mA batteries', '51977', 11],
  ['PSE-10 maximum battery capacity 33 AH', 'LS10227-000NF-E', 9],
  ['ACPS-610 charges 12 to 200 AH batteries', '53018', null],
  ['recuperación de contraseña password agreement', 'Recuperacion de Contraseñas Paneles Notifier', null],
  ['device compatibility document supplement 15378SUP', '15378SUP', null],
  ['SWIFT gateway inalambrico FWSG', 'DN-60820', null],
  ['LCM-320 LEM-320 datasheet lazos', 'DN-6881', null],
  ['SLC wiring manual estilo 4 7', '51253', null],
  ['SLM-318 signaling loop module installation TB1', 'LS10243-000NF-E', null],
  ['PPT08 Convert Node N16 V5.0', 'PPT08', 97],
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
  let fallos = 0;
  for (const [q, doc, pag] of CASOS) {
    await M.ensureIndexesFor(q);
    const r = M.retrieve(q, topk);
    const pos = r.findIndex(d => d.doc === doc && (pag == null || d.page === pag));
    const ok = pos >= 0;
    if (!ok) fallos++;
    console.log(`${ok ? '✓' : '✗'} ${q}  →  ${doc}${pag ? ' p.' + pag : ''}` + (ok ? ` (#${pos + 1})` : `   top: ${r.slice(0, 3).map(d => d.doc + ':' + d.page).join(', ')}`));
  }
  console.log(`\n${CASOS.length - fallos}/${CASOS.length} consultas correctas`);
  process.exit(fallos ? 1 : 0);
})();

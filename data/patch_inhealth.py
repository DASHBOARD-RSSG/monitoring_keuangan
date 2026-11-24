#!/usr/bin/env python3
"""
Patch index.html dashboard RSSG: tambah modul "Laporan Inhealth" + role 'farmasi'.
Pemakaian:  python3 patch_inhealth.py index.html
- Semua perubahan dicek dulu di memori. Jika ada satu titik sisip yang tidak ditemukan,
  skrip BERHENTI dan file Anda tidak diubah.
- Cadangan otomatis: index.html.bak
"""
import re, sys, shutil

path = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
src = open(path, encoding='utf-8').read()


def sisip(anchor, new, where='after'):
    """Sisipkan teks `new` sebelum/sesudah `anchor` (anchor harus muncul tepat 1x)."""
    global src
    n = src.count(anchor)
    assert n == 1, f'Titik sisip ditemukan {n}x (harus 1x): {anchor[:70]!r}'
    src = src.replace(anchor, (anchor + new) if where == 'after' else (new + anchor))


def sisip_re(pola, new_tpl):
    """Sama seperti sisip, tapi dengan regex (toleran terhadap spasi)."""
    global src
    src, n = re.subn(pola, new_tpl, src, count=1, flags=re.S)
    assert n == 1, f'Pola tidak ditemukan: {pola[:70]!r}'


# ───────────────────────── 1. SIDEBAR ─────────────────────────
NAV = r'''<div class="sidebar-section">
    <div class="sidebar-section-label">Laporan Asuransi</div>
    <button class="nav-item" onclick="showPage('inhealth')">
      <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 21s-7-4.5-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 11c0 5.5-7 10-7 10z"/><path d="M9 11h6M12 8v6"/></svg>
      Laporan Inhealth
    </button>
  </div>

  '''
sisip('<div class="sidebar-footer">', NAV, 'before')

# ───────────────────────── 2. HALAMAN ─────────────────────────
PAGE = r'''<!-- ══ PAGE: LAPORAN INHEALTH ══ -->
  <div class="page" id="page-inhealth">
    <div class="kpi-grid" id="kpiInhealth">
      <div class="loading"><div class="spinner"></div> Memuat data...</div>
    </div>

    <div class="section-card" style="margin-bottom:18px">
      <div class="section-head">
        <div>
          <div class="section-title">Filter Laporan Inhealth</div>
          <div class="section-sub">Total Rupiah = total penjualan; Rupiah Kapitasi = pendapatan yang diakui; Selisih = Kapitasi − Total Rupiah (negatif = kapitasi lebih kecil dari total). Klik baris rekap/detail untuk memfilter (klik lagi untuk melepas).</div>
        </div>
      </div>
      <div class="local-filter-wrap">
        <input type="text" id="searchInhealth" placeholder="Cari nama pasien / ID penjualan / ID kunjungan..." oninput="filterInhealthDetail()"/>
        <select id="fltInhealthKategori" onchange="filterInhealthDetail()"><option value="">Semua Kategori</option></select>
        <select id="fltInhealthUnit" onchange="filterInhealthDetail()"><option value="">Semua Unit / Ruangan</option></select>
        <select id="fltInhealthJenis" onchange="filterInhealthDetail()"><option value="">Semua Jenis Penjualan</option></select>
        <select id="fltInhealthLunas" onchange="filterInhealthDetail()"><option value="">Semua Status Lunas</option></select>
        <button class="btn btn-outline" onclick="resetInhealthFilter()">Reset Filter</button>
        <span class="local-filter-count" id="inhealthCount"></span>
      </div>
    </div>

    <div class="grid-2">
      <div class="section-card">
        <div class="section-head"><div class="section-title">Total Rupiah vs Kapitasi per Kategori</div></div>
        <div class="section-body"><div class="chart-wrap"><canvas id="chartInhealthKategori"></canvas></div></div>
      </div>
      <div class="section-card">
        <div class="section-head"><div class="section-title">Tren Total Rupiah vs Kapitasi</div><div class="section-sub">Per hari (1 bulan) atau per bulan (lebih dari 1 bulan)</div></div>
        <div class="section-body"><div class="chart-wrap"><canvas id="chartInhealthTren"></canvas></div></div>
      </div>
    </div>

    <div class="grid-2">
      <div class="section-card">
        <div class="section-head"><div><div class="section-title">Rekap Per Kategori</div><div class="section-sub">Total mengikuti filter aktif</div></div></div>
        <div class="section-body" style="padding:0">
          <div class="tbl-wrap"><table id="tblInhealthKategori">
            <thead id="head-tblInhealthKategori"><tr>
              <th data-key="nama" onclick="tblSort('tblInhealthKategori','nama','text')">Kategori <span class="sort-ico-wrap"></span></th>
              <th class="td-num" data-key="jumlah" onclick="tblSort('tblInhealthKategori','jumlah','number')">Jumlah Baris <span class="sort-ico-wrap"></span></th>
              <th class="td-num" data-key="total" onclick="tblSort('tblInhealthKategori','total','number')">Total Rupiah <span class="sort-ico-wrap"></span></th>
              <th class="td-num" data-key="kapitasi" onclick="tblSort('tblInhealthKategori','kapitasi','number')">Rupiah Kapitasi <span class="sort-ico-wrap"></span></th>
              <th class="td-num" data-key="selisih" onclick="tblSort('tblInhealthKategori','selisih','number')">Selisih <span class="sort-ico-wrap"></span></th>
              <th class="td-num" data-key="persen" onclick="tblSort('tblInhealthKategori','persen','number')">% Kapitasi <span class="sort-ico-wrap"></span></th>
            </tr></thead><tbody></tbody><tfoot></tfoot>
          </table></div>
        </div>
      </div>
      <div class="section-card">
        <div class="section-head"><div><div class="section-title">Rekap Per Unit / Ruangan</div><div class="section-sub">Total mengikuti filter aktif</div></div></div>
        <div class="section-body" style="padding:0">
          <div class="tbl-wrap"><table id="tblInhealthUnit">
            <thead id="head-tblInhealthUnit"><tr>
              <th data-key="nama" onclick="tblSort('tblInhealthUnit','nama','text')">Unit / Ruangan <span class="sort-ico-wrap"></span></th>
              <th class="td-num" data-key="jumlah" onclick="tblSort('tblInhealthUnit','jumlah','number')">Jumlah Baris <span class="sort-ico-wrap"></span></th>
              <th class="td-num" data-key="total" onclick="tblSort('tblInhealthUnit','total','number')">Total Rupiah <span class="sort-ico-wrap"></span></th>
              <th class="td-num" data-key="kapitasi" onclick="tblSort('tblInhealthUnit','kapitasi','number')">Rupiah Kapitasi <span class="sort-ico-wrap"></span></th>
              <th class="td-num" data-key="selisih" onclick="tblSort('tblInhealthUnit','selisih','number')">Selisih <span class="sort-ico-wrap"></span></th>
              <th class="td-num" data-key="persen" onclick="tblSort('tblInhealthUnit','persen','number')">% Kapitasi <span class="sort-ico-wrap"></span></th>
            </tr></thead><tbody></tbody><tfoot></tfoot>
          </table></div>
        </div>
      </div>
    </div>

    <div class="section-card" style="margin-top:18px">
      <div class="section-head">
        <div><div class="section-title">Detail Laporan Inhealth</div><div class="section-sub">Menampilkan maks 2000 baris pertama dari hasil filter; Export Excel mengambil seluruh hasil filter</div></div>
      </div>
      <div class="section-body" style="padding:0">
        <div class="tbl-wrap"><table id="tblInhealthDetail">
          <thead id="head-tblInhealthDetail"><tr>
            <th data-key="_tanggal" onclick="tblSort('tblInhealthDetail','_tanggal','text')">Tanggal <span class="sort-ico-wrap"></span></th>
            <th data-key="nama_rm" onclick="tblSort('tblInhealthDetail','nama_rm','text')">Nama Pasien <span class="sort-ico-wrap"></span></th>
            <th data-key="id_kunjungan" onclick="tblSort('tblInhealthDetail','id_kunjungan','text')">ID Kunjungan <span class="sort-ico-wrap"></span></th>
            <th data-key="_jenis" onclick="tblSort('tblInhealthDetail','_jenis','text')">Jenis Penjualan <span class="sort-ico-wrap"></span></th>
            <th data-key="_kategori" onclick="tblSort('tblInhealthDetail','_kategori','text')">Kategori <span class="sort-ico-wrap"></span></th>
            <th data-key="_unit" onclick="tblSort('tblInhealthDetail','_unit','text')">Unit / Ruangan <span class="sort-ico-wrap"></span></th>
            <th data-key="_lunas" onclick="tblSort('tblInhealthDetail','_lunas','text')">Status Lunas <span class="sort-ico-wrap"></span></th>
            <th class="td-num" data-key="_total" onclick="tblSort('tblInhealthDetail','_total','number')">Total Rupiah <span class="sort-ico-wrap"></span></th>
            <th class="td-num" data-key="_kapitasi" onclick="tblSort('tblInhealthDetail','_kapitasi','number')">Rupiah Kapitasi <span class="sort-ico-wrap"></span></th>
            <th class="td-num" data-key="_selisih" onclick="tblSort('tblInhealthDetail','_selisih','number')">Selisih <span class="sort-ico-wrap"></span></th>
          </tr></thead><tbody></tbody><tfoot></tfoot>
        </table></div>
      </div>
    </div>
  </div>

  '''
sisip('<footer class="app-footer">', PAGE, 'before')

# ───────────────────────── 3. JUDUL HALAMAN ─────────────────────────
sisip("'perbandingan-unit' : ['Biaya vs Pendapatan', 'Analisis per Sub Unit'],",
      "\n  'inhealth'          : ['Laporan Inhealth', 'Total Rupiah vs Kapitasi'],")

# ───────────────────────── 4. CACHE & BATAS BAGIAN ─────────────────────────
sisip('const CACHE_PENDAPATAN_LAIN = {};', '\nconst CACHE_INHEALTH = {};')
sisip('const MAX_BAGIAN_PENDAPATAN_LAIN = 200;', '\nconst MAX_BAGIAN_INHEALTH = 200;')

# ───────────────────────── 5. FETCH PER BULAN ─────────────────────────
sisip('async function loadSemuaUntukRentang(awal, akhir) {',
      "// Inhealth: file data/inhealth-YYYY-MM-pN.json, array 'inhealth_detail'\n"
      "const fetchBulanInhealth = kode => fetchBulanGeneric(CACHE_INHEALTH, kode, 'inhealth', MAX_BAGIAN_INHEALTH, 'inhealth_detail');\n"
      "// Buang baris identik kecuali kolom sinkronisasi (tanggal_sync berubah tiap reload)\n"
      "function dedupeInhealth(rows) {\n"
      "  const seen = new Set(), out = [];\n"
      "  for (const r of rows) { const { tanggal_sync, ...isi } = r; const k = JSON.stringify(isi); if (!seen.has(k)) { seen.add(k); out.push(r); } }\n"
      "  return out;\n}\n\n", 'before')
sisip('pendapatanLainArr = [];', '', 'after')  # cek keberadaan
src = src.replace('pendapatanLainArr = [];', 'pendapatanLainArr = [], inhealthArr = [];', 1)
sisip("if (sumberOk('pendapatanLain')) pendapatanLainArr.push(await fetchBulanPendapatanLain(k));",
      "\n    if (sumberOk('inhealth')) inhealthArr.push(await fetchBulanInhealth(k));")
sisip('pendapatanLain: dedupeExact([].concat(...pendapatanLainArr)),',
      '\n    inhealth: dedupeInhealth([].concat(...inhealthArr)),')

# ───────────────────────── 6. BUILD FILTERED ─────────────────────────
src = src.replace('umPjk, pendapatanLain } = await loadSemuaUntukRentang(awal, akhir);',
                  'umPjk, pendapatanLain, inhealth } = await loadSemuaUntukRentang(awal, akhir);', 1)
assert 'pendapatanLain, inhealth }' in src, 'Destructuring loadSemuaUntukRentang tidak ditemukan'
sisip("const pendapatanLainRows = pendapatanLain.filter(r => inRange(r.tanggal_sub_transaksi, awal, akhir));",
      "\n  const inhealthRows = (inhealth || []).filter(r => inRange(r.tanggal_penjualan || r.tgl_kunjungan, awal, akhir));")
sisip('pendapatan_lain_detail: pendapatanLainRows,', '\n    inhealth_detail: inhealthRows,')

# ───────────────────────── 7. RENDER PAGE ─────────────────────────
sisip_re(r"(case 'perbandingan-unit':\s+renderPerbandinganUnit\(\);\s+break;)",
         r"\1\n    case 'inhealth':           renderInhealth(d);          break;")

# ───────────────────────── 8. MODUL JS ─────────────────────────
JS = r'''// ══ MODUL LAPORAN INHEALTH ══
// Sesuaikan di sini bila kolom yang dianggap "Total Rupiah" / "Kapitasi" berbeda.
const INHEALTH_FIELD_TOTAL    = 'total_penjualan'; // Total Rupiah
const INHEALTH_FIELD_KAPITASI = 'pendapatan';      // Rupiah Kapitasi (pendapatan yang diakui)
// Selisih = Kapitasi - Total Rupiah  (negatif = kapitasi lebih kecil dari total)

let currentInhealth = [];
const INH_REKAP_LAST = {};
const escInh = s => String(s ?? '-').replace(/[&<>"]/g, c => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' }[c]));

function olahInhealth(rows) {
  return rows.map(r => {
    const total = parseFloat(r[INHEALTH_FIELD_TOTAL]) || 0;
    const kap   = parseFloat(r[INHEALTH_FIELD_KAPITASI]) || 0;
    return {
      ...r,
      _tanggal : String(r.tanggal_penjualan || r.tgl_kunjungan || '').substring(0,10),
      _kategori: r.kategori || 'Tanpa Kategori',
      _unit    : r.sub_unit || r.ruangan_terakhir || r.poliklinik || 'Tidak diketahui',
      _jenis   : r.jenis_penjualan || '-',
      _lunas   : r.status_lunas || '-',
      _total   : total,
      _kapitasi: kap,
      _selisih : kap - total,
    };
  });
}

function renderInhealth(d) {
  currentInhealth = olahInhealth(d.inhealth_detail || []);
  populateInhealthFilterOptions();
  filterInhealthDetail();
}

function populateInhealthFilterOptions() {
  const fill = (id, values, label) => {
    const el = document.getElementById(id);
    if (!el) return;
    const cur = el.value;
    const opts = [...new Set(values.filter(v => v && v !== '-'))].sort((a,b) => String(a).localeCompare(String(b), 'id'));
    el.innerHTML = `<option value="">${label}</option>` + opts.map(v => `<option value="${escInh(v)}">${escInh(v)}</option>`).join('');
    if (opts.includes(cur)) el.value = cur;
  };
  fill('fltInhealthKategori', currentInhealth.map(r => r._kategori), 'Semua Kategori');
  fill('fltInhealthUnit',     currentInhealth.map(r => r._unit),     'Semua Unit / Ruangan');
  fill('fltInhealthJenis',    currentInhealth.map(r => r._jenis),    'Semua Jenis Penjualan');
  fill('fltInhealthLunas',    currentInhealth.map(r => r._lunas),    'Semua Status Lunas');
}

function rekapInhealth(rows, field) {
  const map = {};
  rows.forEach(r => {
    const k = r[field] || 'Lainnya';
    const x = map[k] || (map[k] = { nama: k, jumlah: 0, total: 0, kapitasi: 0 });
    x.jumlah += 1; x.total += r._total; x.kapitasi += r._kapitasi;
  });
  return Object.values(map).map(x => ({ ...x, selisih: x.kapitasi - x.total, persen: x.total ? x.kapitasi / x.total * 100 : 0 }))
    .sort((a,b) => b.total - a.total);
}

function renderInhealthRekapTable(tableId, rows, filterId) {
  INH_REKAP_LAST[tableId] = { rows, filterId };
  const sorted = tblApplySort(tableId, rows);
  document.querySelector(`#${tableId} tbody`).innerHTML = sorted.map(r => `
    <tr ${rfAttr([[filterId, r.nama]])}>
      <td style="font-size:11px">${escInh(r.nama)}</td>
      <td class="td-num">${num(r.jumlah)}</td>
      <td class="td-num td-bold">${rupiah(r.total)}</td>
      <td class="td-num">${rupiah(r.kapitasi)}</td>
      <td class="td-num ${r.selisih < 0 ? 'rekon-diff' : 'rekon-match'}">${rupiah(r.selisih)}</td>
      <td class="td-num">${r.total ? r.persen.toFixed(1) + '%' : '-'}</td>
    </tr>`).join('') || '<tr><td colspan="6" class="empty">Tidak ada data</td></tr>';
  const tt = sumBy(sorted, 'total'), tk = sumBy(sorted, 'kapitasi');
  document.querySelector(`#${tableId} tfoot`).innerHTML = sorted.length ? tblTotalRow(1, [
    { value: sumBy(sorted, 'jumlah'), type: 'num' },
    { value: tt, type: 'rupiah' },
    { value: tk, type: 'rupiah' },
    { value: tk - tt, type: 'rupiah' },
    { value: tt ? tk / tt * 100 : 0, type: 'percent' },
  ]) : '';
  tblRefreshIcons(tableId, `head-${tableId}`);
}

function filterInhealthDetail() {
  const q      = (document.getElementById('searchInhealth')?.value || '').trim().toLowerCase();
  const kat    = document.getElementById('fltInhealthKategori')?.value || '';
  const unit   = document.getElementById('fltInhealthUnit')?.value || '';
  const jenis  = document.getElementById('fltInhealthJenis')?.value || '';
  const lunas  = document.getElementById('fltInhealthLunas')?.value || '';

  let rows = currentInhealth.filter(r => {
    if (q && !([r.nama_rm, r.id_penjualan, r.id_kunjungan, r.idgl, r.nomor_rm].some(v => String(v ?? '').toLowerCase().includes(q)))) return false;
    if (kat   && r._kategori !== kat)   return false;
    if (unit  && r._unit !== unit)      return false;
    if (jenis && r._jenis !== jenis)    return false;
    if (lunas && r._lunas !== lunas)    return false;
    return true;
  });
  rows = tblApplySort('tblInhealthDetail', rows);

  document.getElementById('inhealthCount').textContent = `${num(rows.length)} dari ${num(currentInhealth.length)} baris`;

  // ── KPI ──
  const totalRp = sumBy(rows, '_total'), totalKap = sumBy(rows, '_kapitasi'), selisih = totalKap - totalRp;
  const nKunjungan = new Set(rows.map(r => r.id_kunjungan).filter(Boolean)).size;
  document.getElementById('kpiInhealth').innerHTML = `
    <div class="kpi-card blue"><div class="kpi-label">Total Rupiah</div><div class="kpi-value">${rupiah(totalRp)}</div><div class="kpi-sub">${num(rows.length)} baris terfilter</div></div>
    <div class="kpi-card green"><div class="kpi-label">Rupiah Kapitasi</div><div class="kpi-value">${rupiah(totalKap)}</div><div class="kpi-sub">${totalRp ? (totalKap / totalRp * 100).toFixed(1) + '% dari total rupiah' : '-'}</div></div>
    <div class="kpi-card ${selisih < 0 ? 'red' : 'purple'}"><div class="kpi-label">Selisih (Kapitasi − Total)</div><div class="kpi-value">${rupiah(selisih)}</div><div class="kpi-sub">${selisih < 0 ? 'kapitasi lebih kecil dari total' : 'kapitasi ≥ total rupiah'}</div></div>
    <div class="kpi-card amber"><div class="kpi-label">Jumlah Kunjungan</div><div class="kpi-value">${num(nKunjungan)}</div><div class="kpi-sub">ID kunjungan unik</div></div>`;

  // ── Rekap (dihitung dari baris terfilter) ──
  const perKategori = rekapInhealth(rows, '_kategori');
  const perUnit     = rekapInhealth(rows, '_unit');
  renderInhealthRekapTable('tblInhealthKategori', perKategori, 'fltInhealthKategori');
  renderInhealthRekapTable('tblInhealthUnit',     perUnit,     'fltInhealthUnit');

  // ── Grafik per kategori ──
  destroyChart('chartInhealthKategori');
  const c1 = document.getElementById('chartInhealthKategori');
  if (c1) {
    CHARTS['chartInhealthKategori'] = new Chart(c1, {
      type: 'bar',
      data: {
        labels: perKategori.map(r => String(r.nama).substring(0, 22)),
        datasets: [
          { label: 'Total Rupiah',    data: perKategori.map(r => r.total),    backgroundColor: '#2563eb', borderRadius: 4 },
          { label: 'Rupiah Kapitasi', data: perKategori.map(r => r.kapitasi), backgroundColor: '#059669', borderRadius: 4 },
        ]
      },
      options: CHART_DEFAULTS
    });
  }

  // ── Grafik tren: per hari bila 1 bulan, per bulan bila lebih ──
  const bulanSet = new Set(rows.map(r => r._tanggal.substring(0, 7)).filter(Boolean));
  const panjang = bulanSet.size > 1 ? 7 : 10;
  const tren = {};
  rows.forEach(r => {
    const k = r._tanggal.substring(0, panjang); if (!k) return;
    const x = tren[k] || (tren[k] = { total: 0, kap: 0 });
    x.total += r._total; x.kap += r._kapitasi;
  });
  const labels = Object.keys(tren).sort();
  makeLine('chartInhealthTren', labels.map(l => panjang === 10 ? l.substring(5) : l), [
    { label: 'Total Rupiah',    data: labels.map(l => tren[l].total), borderColor: '#2563eb', backgroundColor: 'rgba(37,99,235,.06)', fill: true, tension: .3, pointRadius: 2, borderWidth: 2 },
    { label: 'Rupiah Kapitasi', data: labels.map(l => tren[l].kap),   borderColor: '#059669', backgroundColor: 'rgba(5,150,105,.06)', fill: true, tension: .3, pointRadius: 2, borderWidth: 2 },
  ]);

  // ── Detail ──
  document.querySelector('#tblInhealthDetail tbody').innerHTML = rows.slice(0, 2000).map(r => `
    <tr ${rfAttr([['fltInhealthKategori', r._kategori], ['fltInhealthUnit', r._unit]])}>
      <td>${escInh(r._tanggal)}</td>
      <td>${escInh(r.nama_rm)}</td>
      <td style="font-size:11px">${escInh(r.id_kunjungan)}</td>
      <td style="font-size:11px">${escInh(r._jenis)}</td>
      <td><span class="badge ${/kapitasi/i.test(r._kategori) ? 'badge-green' : 'badge-blue'}">${escInh(r._kategori)}</span></td>
      <td style="font-size:11px">${escInh(r._unit)}</td>
      <td><span class="badge ${r._lunas === 'Lunas' ? 'badge-green' : 'badge-amber'}">${escInh(r._lunas)}</span></td>
      <td class="td-num">${rupiah(r._total)}</td>
      <td class="td-num">${rupiah(r._kapitasi)}</td>
      <td class="td-num td-bold ${r._selisih < 0 ? 'rekon-diff' : ''}">${rupiah(r._selisih)}</td>
    </tr>`).join('') || '<tr><td colspan="10" class="empty">Tidak ada data</td></tr>';
  document.querySelector('#tblInhealthDetail tfoot').innerHTML = rows.length ? tblTotalRow(7, [
    { value: totalRp,  type: 'rupiah' },
    { value: totalKap, type: 'rupiah' },
    { value: selisih,  type: 'rupiah' },
  ]) : '';
  tblRefreshIcons('tblInhealthDetail', 'head-tblInhealthDetail');
}

function resetInhealthFilter() {
  ['searchInhealth','fltInhealthKategori','fltInhealthUnit','fltInhealthJenis','fltInhealthLunas'].forEach(id => document.getElementById(id).value = '');
  filterInhealthDetail();
}

TblRerender.tblInhealthDetail = filterInhealthDetail;
['tblInhealthKategori', 'tblInhealthUnit'].forEach(id => {
  TblRerender[id] = () => { const st = INH_REKAP_LAST[id]; if (st) renderInhealthRekapTable(id, st.rows, st.filterId); };
});

'''
sisip('async function loadManifest() {', JS, 'before')

# ───────────────────────── 9. HAK AKSES ─────────────────────────
# pprp: tambah halaman & sumber inhealth
sisip("'biaya-rkap','perbandingan-unit'], sumber: ['biayaBahan','biayaUmum','biayaUmumBaru','aux']",
      '', 'after')
src = src.replace("'biaya-rkap','perbandingan-unit'], sumber: ['biayaBahan','biayaUmum','biayaUmumBaru','aux']",
                  "'biaya-rkap','perbandingan-unit','inhealth'], sumber: ['biayaBahan','biayaUmum','biayaUmumBaru','aux','inhealth']", 1)
assert "'perbandingan-unit','inhealth']" in src, 'Konfigurasi role pprp tidak ditemukan'

# farmasi: seluruh biaya + inhealth  (admin & akuntansi sudah null = akses semua halaman/sumber)
sisip("/personalia/i, awal: 'biaya-umum' },",
      "\n  farmasi:   { label: 'Farmasi',   halaman: ['biaya-bahan','biaya-umum','biaya-umum-baru','inhealth'], sumber: ['biayaBahan','biayaUmum','biayaUmumBaru','inhealth'], subUnit: null, awal: 'biaya-bahan' },")

# email cadangan
sisip_re(r"('admin@ptcn\.id'\s*:\s*'admin',)", r"\1\n  'farmasi@ptcn.id'   : 'farmasi',")

# ───────────────────────── TULIS HASIL ─────────────────────────
shutil.copyfile(path, path + '.bak')
open(path, 'w', encoding='utf-8').write(src)
print('Selesai. Cadangan:', path + '.bak')

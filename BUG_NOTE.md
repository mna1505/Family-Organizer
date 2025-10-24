# Catatan Bug
## Front-end
- Saat submit formulir namun terdapat lebih dari satu pesan error, pesan error tersebut tertumpuk di satu tempat pada halaman input pemasukan dan pengeluaran
- Tombol tambah tugas seharusnya dihilangkan untuk member (dapat dibenahi dengan menambah if else) (ok)
- Tombol hapus tugas seharusnya dihilangkan untuk member (dapat dibenahi dengan menambah if else) (ok)
- Tombol menu titik tiga pada list user seharusnya dihilangkan untuk member (dapat dibenahi dengan menambah if else) (ok)
- Barang tidak memiliki tombol hapus, seharusnya ada (ok)

## Back-end
- Saat menambah tugas lalu ditugaskan oleh pengguna bernama A. Saat A diubah perannya, tugas yang ditugaskan kepada A malah menghilang dari halaman semua user dalam satu keluarga namun masih ada di database (ok)
- Saat menambah input pemasukan/pengeluaran lalu pelakunya diset ke A. Saat A diubah perannya, semua catatan keuangan dengan pelaku A hilang (ok)
- Admin seharusnya dapat melihat semua tugas meskipun tidak ditugaskan kepada admin. Tapi admin tidak dapat menyelesaikannya jika tidak ditugaskan
- Member seharusnya tidak bisa menghapus tugas (ok)
- Tanggal transaksi seharusnya diurutkan secara descending (terbaru ke terlama) [gak penting]

## permasalahan sosial

semisal ya, ada 2 user, mereka itu adek kakak, mereka ini tiba-tiba saling bermusuhan, terus si kakak nyoba memalsukan pengeluaran besar dengan atas nama adek nya, maka ini akan menjadi permasalahan yang cukup rumit, karena bisa jadi orang tua mereka akan salah paham dan menyalahkan si adek, padahal pelaku nya adalah kakak.
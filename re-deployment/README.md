1. Monitoring Metrik Model Secara Berkala.
Sistem akan mengevaluasi performa model secara berkala menggunakan data terbaru. Metrik model (misalnya accuracy, F1-score, atau loss) akan dicatat dalam MLflow Tracking.

2. Trigger Otomatis Jika Metrik Model Turun.
Jika metrik model turun di bawah ambang batas tertentu, sistem akan menandai model sebagai "perlu diperbarui". Ambang batas ini bisa berupa:

   - Accuracy < 85%

   - F1-score turun lebih dari 5% dalam 7 hari terakhir

   - AUC-ROC di bawah 0.8

3. Melatih Model Baru.
Jika model lama mengalami degradasi performa, sistem akan secara otomatis mengambil data terbaru dan melatih ulang model baru.

4. Validasi Model Baru.
Model baru diuji dan dibandingkan dengan model lama. Jika model baru memiliki performa yang lebih baik, model ini akan di-deploy.

5. Deployment Model Baru ke Produksi.
Model baru menggantikan model lama dalam MLflow Model Registry. Sistem mengarahkan permintaan inferensi ke model baru tanpa mengganggu layanan yang sedang berjalan.

6. Menyimpan Model Lama sebagai Cadangan.
Model lama tetap disimpan dalam MLflow Registry sebagai cadangan jika sewaktu-waktu model baru perlu dikembalikan.
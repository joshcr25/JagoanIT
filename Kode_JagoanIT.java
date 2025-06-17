import java.io.IOException;
import javax.swing.*;

public class Kode_JagoanIT {
    public static void main(String[] args) {
        // Jalankan aplikasi di Event Dispatch Thread (EDT) Swing
        SwingUtilities.invokeLater(() -> {
            try {
                TrainSchedule schedule = new TrainSchedule("train_schedule_Jabodetabek.csv");
                TrainSchedulePredictorApp app = new TrainSchedulePredictorApp(schedule);
                TrainScheduleGUI gui = new TrainScheduleGUI(app);
                gui.setVisible(true);
            } catch (IOException e) {
                JOptionPane.showMessageDialog(null,
                        "Gagal memuat jadwal kereta (train_schedule_Jabodetabek.csv): " + e.getMessage(), "Fatal Error",
                        JOptionPane.ERROR_MESSAGE);
                e.printStackTrace();
            } catch (Exception e) {
                JOptionPane.showMessageDialog(null, "Terjadi kesalahan yang tidak terduga: " + e.getMessage(),
                        "Fatal Error", JOptionPane.ERROR_MESSAGE);
                e.printStackTrace();
            }
        });
    }
}
/**
 * KELAS BARU: TrainRouteRenderer
 * Renderer tabel kustom untuk mewarnai baris berdasarkan nama kereta.
 */


import java.awt.Color;
import java.awt.Component;
import java.awt.Font;
import javax.swing.JTable;
import javax.swing.SwingConstants;
import javax.swing.table.DefaultTableCellRenderer;

public class TrainRouteRenderer extends DefaultTableCellRenderer {
    // Definisikan warna di sini
    private static final Color BOGOR_COLOR = Color.decode("#E30A16");
    private static final Color CIKARANG_COLOR = Color.decode("#0084D8");
    private static final Color TANJUNG_PRIOK_COLOR = Color.decode("#DD0067");
    private static final Color RANGKASBITUNG_COLOR = Color.decode("#16812B");
    private static final Color TANGERANG_COLOR = Color.decode("#623814");
    private static final Color TRANSIT_COLOR = new Color(220, 220, 220); // Abu-abu muda untuk transit

    @Override
    public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus,
            int row, int column) {
        Component c = super.getTableCellRendererComponent(table, value, isSelected, hasFocus, row, column);

        // Ambil nama kereta dari kolom pertama (indeks 0)
        String trainName = (String) table.getValueAt(row, 0);

        if (trainName == null) {
            c.setBackground(table.getBackground());
            c.setForeground(table.getForeground());
            return c;
        }

        // Tentukan warna berdasarkan nama kereta
        Color rowColor = table.getBackground(); // Warna default
        if (trainName.toLowerCase().contains("bogor")) {
            rowColor = BOGOR_COLOR;
        } else if (trainName.toLowerCase().contains("cikarang")) {
            rowColor = CIKARANG_COLOR;
        } else if (trainName.toLowerCase().contains("tanjung priok")) {
            rowColor = TANJUNG_PRIOK_COLOR;
        } else if (trainName.toLowerCase().contains("rangkasbitung")) {
            rowColor = RANGKASBITUNG_COLOR;
        } else if (trainName.toLowerCase().contains("tangerang")) {
            rowColor = TANGERANG_COLOR;
        } else if (trainName.contains("TRANSIT") || trainName.contains("ALTERNATIF")) {
            rowColor = TRANSIT_COLOR;
        }

        c.setBackground(rowColor);

        // Atur warna teks agar kontras dengan latar belakang
        // Jika warna latar terlalu gelap, buat teks menjadi putih
        if (rowColor.equals(BOGOR_COLOR) || rowColor.equals(RANGKASBITUNG_COLOR) || rowColor.equals(TANGERANG_COLOR)) {
            c.setForeground(Color.WHITE);
        } else {
            c.setForeground(Color.BLACK);
        }

        // Khusus untuk baris transit/alternatif
        if (trainName.contains("TRANSIT") || trainName.contains("ALTERNATIF")) {
            c.setFont(new Font("SansSerif", Font.BOLD | Font.ITALIC, 12));
            setHorizontalAlignment(SwingConstants.CENTER);
        } else {
            c.setFont(table.getFont());
            setHorizontalAlignment(SwingConstants.LEFT);
        }

        if (isSelected) {
            c.setBackground(table.getSelectionBackground());
            c.setForeground(table.getSelectionForeground());
        }

        return c;
    }
}
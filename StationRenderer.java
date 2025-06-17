import java.awt.Component;
import java.util.Map;
import javax.swing.DefaultListCellRenderer;
import javax.swing.JList;

/**
 * Renderer kustom untuk menampilkan nama stasiun
 * dan mengatur tooltip berisi alamat stasiun.
 */
public class StationRenderer extends DefaultListCellRenderer {

    private final Map<String, String> stationAddresses;

    public StationRenderer(Map<String, String> stationAddresses) {
        this.stationAddresses = stationAddresses;
    }

    @Override
    public Component getListCellRendererComponent(JList<?> list, Object value, int index, boolean isSelected, boolean cellHasFocus) {
        // Panggil implementasi default untuk mendapatkan tampilan dasar (JLabel)
        super.getListCellRendererComponent(list, value, index, isSelected, cellHasFocus);

        // 'value' adalah nama stasiun (misal: "Tanah Abang")
        if (value != null) {
            String stationName = value.toString();
            // Ambil alamat dari Map berdasarkan nama stasiun
            String address = stationAddresses.get(stationName);

            // Jika alamat ditemukan, atur sebagai tooltip
            if (address != null) {
                setToolTipText(address);
            } else {
                setToolTipText(null); // Tidak ada tooltip jika alamat tidak ada
            }
        }
        return this;
    }
}
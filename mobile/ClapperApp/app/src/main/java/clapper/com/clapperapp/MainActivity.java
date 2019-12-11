package clapper.com.clapperapp;

import android.graphics.Bitmap;
import android.support.annotation.RequiresPermission;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;

import com.google.zxing.BarcodeFormat;
import com.google.zxing.MultiFormatWriter;
import com.google.zxing.WriterException;
import com.google.zxing.common.BitMatrix;

import java.util.ArrayList;

public class MainActivity extends AppCompatActivity {

    int scene;
    int take;
    ImageView qrDisplay;
    Button nextScene;
    Button nextTake;
    Button prevScene;
    Button prevTake;
    TextView header;
    ArrayList<ArrayList<Bitmap>> savedCodes;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        qrDisplay = findViewById(R.id.qrDisplay);
        nextScene = findViewById(R.id.nextSceneButton);
        nextTake = findViewById(R.id.nextTakeButton);
        prevScene = findViewById(R.id.prevSceneButton);
        prevTake = findViewById(R.id.prevTakeButton);
        header = findViewById(R.id.headerView);

        scene = 1;
        take = 1;

        savedCodes = new ArrayList<>();
        savedCodes.add(new ArrayList<Bitmap>());

        try {
            savedCodes.get(0).add(getQR(scene, take));
        } catch (WriterException e) {
            System.out.println("Could not initialize QR Code:");
            e.printStackTrace();
        }

        qrDisplay.setImageBitmap(savedCodes.get(0).get(0));

        nextScene.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {

                scene++;
                take = 1;

                if (scene > savedCodes.size()) {
                    savedCodes.add(new ArrayList<Bitmap>());
                }

                if (take > savedCodes.get(scene-1).size()) {
                    try {
                        savedCodes.get(scene-1).add(getQR(scene, take));
                    } catch (WriterException e) {
                        System.out.println("Could not update QR Code:");
                        e.printStackTrace();
                    }
                }

                qrDisplay.setImageBitmap(savedCodes.get(scene-1).get(take-1));
                updateHeader();
            }
        });

        prevScene.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {

                if (scene > 1) {
                    scene--;
                    take = 1;
                }

                qrDisplay.setImageBitmap(savedCodes.get(scene-1).get(take-1));
                updateHeader();

            }
        });

        nextTake.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {

                take++;

                if (take > savedCodes.get(scene-1).size()) {
                    try {
                        savedCodes.get(scene-1).add(getQR(scene, take));
                    } catch (WriterException e) {
                        System.out.println("Could not update QR Code:");
                        e.printStackTrace();
                    }
                }

                qrDisplay.setImageBitmap(savedCodes.get(scene-1).get(take-1));
                updateHeader();

            }
        });

        prevTake.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {

                if (take > 1) {
                    take--;
                }

                qrDisplay.setImageBitmap(savedCodes.get(scene-1).get(take-1));
                updateHeader();

            }
        });
    }

    void updateHeader() {
        header.setText("Scene " + scene + ", Take " + take);
    }

    Bitmap getQR(int scene, int take) throws WriterException {
        BitMatrix bitMatrix;
        try {
            bitMatrix = new MultiFormatWriter().encode(
                    (scene + ":" + take),
                    BarcodeFormat.DATA_MATRIX.QR_CODE,
                    500, 500, null
            );

        } catch (IllegalArgumentException Illegalargumentexception) {

            return null;
        }
        int bitMatrixWidth = bitMatrix.getWidth();

        int bitMatrixHeight = bitMatrix.getHeight();

        int[] pixels = new int[bitMatrixWidth * bitMatrixHeight];

        for (int y = 0; y < bitMatrixHeight; y++) {
            int offset = y * bitMatrixWidth;

            for (int x = 0; x < bitMatrixWidth; x++) {

                pixels[offset + x] = bitMatrix.get(x, y) ?
                        getResources().getColor(R.color.qrcontent):getResources().getColor(R.color.qrback);
            }
        }
        Bitmap bitmap = Bitmap.createBitmap(bitMatrixWidth, bitMatrixHeight, Bitmap.Config.ARGB_4444);

        bitmap.setPixels(pixels, 0, 500, 0, 0, bitMatrixWidth, bitMatrixHeight);
        return bitmap;
    }
}

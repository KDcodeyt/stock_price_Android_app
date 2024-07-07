package com.example.test4;

import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;
import android.os.AsyncTask;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;
import org.json.JSONException;
import org.json.JSONObject;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import android.widget.TextView;

public class MainActivity extends AppCompatActivity {

    private EditText editTextStock;
    private EditText editTextNumDays;
    private Button buttonPredict;
    private static TextView textViewResponse;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Initialize UI components
        editTextStock = findViewById(R.id.editTextStock);
        editTextNumDays = findViewById(R.id.editTextNumDays);
        buttonPredict = findViewById(R.id.buttonPredict);
        textViewResponse = findViewById(R.id.textViewResponse);

        // Button click listener
        buttonPredict.setOnClickListener(view -> {
            String stock = editTextStock.getText().toString();
            int numDays = Integer.parseInt(editTextNumDays.getText().toString());
            // Call predictStock function
            predictStock(stock, numDays);
        });
    }

    // Function to make API request
    private void predictStock(String stock, int numDays) {
        new PredictStockTask(stock, numDays).execute();
    }

    private class PredictStockTask extends AsyncTask<Void, Void, String> {

        private final String stock;
        private final int numDays;

        public PredictStockTask(String stock, int numDays) {
            this.stock = stock;
            this.numDays = numDays;
        }

        @Override
        protected String doInBackground(Void... voids) {
            HttpURLConnection urlConnection = null;
            BufferedReader reader = null;
            String jsonString = null;

            try {
                // Construct the URL for the API call
                URL url = new URL("http://10.67.118.112:5000/predict?stock=" + stock + "&num_days=" + numDays);
                urlConnection = (HttpURLConnection) url.openConnection();
                urlConnection.setRequestMethod("GET");

                // Read the input stream into a String
                StringBuilder stringBuilder = new StringBuilder();
                reader = new BufferedReader(new InputStreamReader(urlConnection.getInputStream()));

                String line;
                while ((line = reader.readLine()) != null) {
                    stringBuilder.append(line).append("\n");
                }

                if (stringBuilder.length() == 0) {
                    return null; // Empty response
                }

                jsonString = stringBuilder.toString();
            } catch (IOException e) {
                e.printStackTrace();
            } finally {
                // Close resources
                if (urlConnection != null) {
                    urlConnection.disconnect();
                }
                if (reader != null) {
                    try {
                        reader.close();
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                }
            }

            return jsonString;
        }

        @Override
        protected void onPostExecute(String result) {
            if (result != null) {
                try {
                    JSONObject jsonResponse = new JSONObject(result);
                    System.out.println("JSONResponse : "+jsonResponse);
                    JSONObject jsonResponse_future_predictions = jsonResponse.getJSONObject("future_predictions");
                    System.out.println("jsonResponse_future_predictions : "+jsonResponse_future_predictions);
                    StringBuilder formattedResponse = new StringBuilder();

                    for (int i = 1; i < jsonResponse_future_predictions.length()+1; i++) {
                        String day = "day_"+Integer.toString(i);
                        String next_day_prediction = jsonResponse_future_predictions.getString(day);
                        System.out.println("next_day_prediction : "+next_day_prediction);
                        formattedResponse.append("Day "+i+": ").append(next_day_prediction).append("\n\n");
                    }

                    textViewResponse.setText(formattedResponse.toString());
                } catch (JSONException e) {
                    e.printStackTrace();
                }
            } else {
                Toast.makeText(MainActivity.this, "Failed to fetch data", Toast.LENGTH_SHORT).show();
            }
        }
    }
}

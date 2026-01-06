document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("predict-form");
  const resultDiv = document.getElementById("result");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    // Read values
    const startupAge = Number(document.getElementById("startup_age").value);
    const relationships = Number(document.getElementById("relationships").value);

    // Safety check (no negatives)
    if (startupAge < 0 || relationships < 0) {
      resultDiv.textContent = "❌ Values cannot be negative.";
      return;
    }

    // Show loading
    resultDiv.classList.remove("result-placeholder");
    resultDiv.textContent = "⏳ Predicting...";

    // Payload for Flask
    const payload = {
      startup_age: startupAge,
      relationships: relationships,
      category: document.getElementById("category").value,
      state: document.getElementById("state").value,

      has_vc: document.getElementById("has_vc").checked,
      has_angel: document.getElementById("has_angel").checked,
      has_roundA: document.getElementById("has_series_a").checked,
      is_top500: document.getElementById("is_top500").checked,
    };

    try {
      const response = await fetch("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Prediction failed");

      // Show real model result
      resultDiv.innerHTML = `
        <strong>Prediction:</strong> ${data.prediction}<br>
        <strong>Success Probability:</strong> ${(data.success_probability * 100).toFixed(1)}%<br>
        <strong>Risk Level:</strong> ${data.risk_level}
      `;
    } catch (err) {
      resultDiv.textContent = "❌ Error during prediction.";
      console.error(err);
    }
  });
});

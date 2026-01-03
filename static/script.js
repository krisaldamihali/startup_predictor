document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("predict-form");
  const resultDiv = document.getElementById("result");

  const probabilityEl = document.getElementById("metric-probability");
  const riskEl = document.getElementById("metric-risk");
  const confidenceEl = document.getElementById("metric-confidence");
  const commentEl = document.getElementById("result-comment");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    resultDiv.classList.remove("result-placeholder");
    resultDiv.classList.remove("error");
    resultDiv.textContent = "⏳ Analyzing...";

    if (probabilityEl) probabilityEl.textContent = "—";
    if (riskEl) riskEl.textContent = "—";
    if (confidenceEl) confidenceEl.textContent = "—";
    if (commentEl) commentEl.textContent = "Waiting for prediction...";

    const payload = {
      funding_total: Number(document.getElementById("funding_total").value),
      funding_rounds: Number(document.getElementById("funding_rounds").value),
      startup_age: Number(document.getElementById("startup_age").value),
      milestones: Number(document.getElementById("milestones").value),
      relationships: Number(document.getElementById("relationships").value),
      avg_participants: Number(document.getElementById("avg_participants").value),

      // these MUST match your model one-hot flags
      category: document.getElementById("category").value, // software/web/mobile/enterprise/...
      state: document.getElementById("state") ? document.getElementById("state").value : "other", // CA/NY/MA/TX/other

      has_vc: document.getElementById("has_vc").checked,
      has_angel: document.getElementById("has_angel").checked,
      has_roundA: document.getElementById("has_series_a").checked, // keep UI id, map to has_roundA
      is_top500: document.getElementById("is_top500").checked,
    };

    try {
      const response = await fetch("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Server error");

      // NO fallbacks
      const probability = data.success_probability;
      const prediction = data.prediction;
      const confidence = data.confidence;
      const risk = data.risk_level;

      if (
        probability === undefined ||
        prediction === undefined ||
        confidence === undefined ||
        risk === undefined
      ) {
        throw new Error("Invalid API response (missing keys).");
      }

      resultDiv.innerHTML = `
        <div><strong>🎯 Prediction:</strong> ${prediction}</div>
        <div><strong>Success Probability:</strong> ${(probability * 100).toFixed(1)}%</div>
        <div>${
          probability >= 0.6
            ? "✅ Strong indicators for acquisition or successful exit."
            : "⚠️ May face challenges based on current metrics."
        }</div>
      `;

      if (probabilityEl) probabilityEl.textContent = `${(probability * 100).toFixed(1)}%`;
      if (riskEl) riskEl.textContent = risk;
      if (confidenceEl) confidenceEl.textContent = `${(confidence * 100).toFixed(0)}%`;

      if (commentEl) {
        commentEl.textContent =
          "Prediction is computed from your input features using the trained model.";
      }
    } catch (err) {
      console.error(err);
      resultDiv.classList.add("error");
      resultDiv.textContent = `❌ Error: ${err.message}`;
      if (commentEl) commentEl.textContent = "Please check inputs and try again.";
    }
  });
});

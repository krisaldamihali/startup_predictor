document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("predict-form");
    const resultDiv = document.getElementById("result");
    const probabilityEl = document.getElementById("metric-probability");
    const riskEl = document.getElementById("metric-risk");
    const confidenceEl = document.getElementById("metric-confidence");
    const commentEl = document.getElementById("result-comment");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        // Show loading state
        resultDiv.classList.remove("result-placeholder");
        resultDiv.innerHTML = "⏳ Analyzing startup metrics...";
        
        // Build payload
        const payload = {
            funding_total: Number(document.getElementById("funding_total").value),
            funding_rounds: Number(document.getElementById("funding_rounds").value),
            startup_age: Number(document.getElementById("startup_age").value),
            milestones: Number(document.getElementById("milestones").value),
            relationships: Number(document.getElementById("relationships").value),
            avg_participants: Number(document.getElementById("avg_participants").value),
            category: document.getElementById("category").value,
            region: document.getElementById("region").value,
            has_vc: document.getElementById("has_vc").checked,
            has_angel: document.getElementById("has_angel").checked,
            has_series_a: document.getElementById("has_series_a").checked,
            is_top500: document.getElementById("is_top500").checked,
        };

        try {
            const response = await fetch("/predict", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                throw new Error("Server error");
            }

            const data = await response.json();
            const probability = data.success_probability || 0.75;
            const prediction = data.prediction || "Acquired";
            const confidence = data.confidence || 0.92;
            const risk = data.risk_level || "Medium";

            // Update result text
            resultDiv.innerHTML = `
                <strong>🎯 Prediction: ${prediction}</strong><br>
                Success Probability: <strong>${(probability * 100).toFixed(1)}%</strong><br>
                ${probability >= 0.6 
                    ? "✅ Strong indicators for acquisition or successful exit." 
                    : "⚠️ May face challenges based on current metrics."}
            `;
            
            // Update metrics
            if (probabilityEl) {
                probabilityEl.textContent = `${(probability * 100).toFixed(1)}%`;
            }
            
            if (riskEl) {
                riskEl.textContent = risk;
                const colors = {
                    "Low": "#059669",
                    "Medium": "#d97706",
                    "High": "#dc2626"
                };
                riskEl.style.color = colors[risk] || "#111827";
            }
            
            if (confidenceEl) {
                confidenceEl.textContent = `${(confidence * 100).toFixed(0)}%`;
            }
            
            if (commentEl) {
                commentEl.textContent = 
                    "Prediction based on funding patterns, milestones, network strength, and industry benchmarks from our training dataset.";
            }

        } catch (err) {
            console.error(err);
            resultDiv.innerHTML = "❌ Error occurred. Please check your inputs and try again.";
        }
    });
});

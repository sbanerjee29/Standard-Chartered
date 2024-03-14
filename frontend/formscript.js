// Add JavaScript to handle multi-step form and progress bar

document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("multi-step-form");
    const steps = form.querySelectorAll(".step");
    const progressBar = document.getElementById("progress");
    let currentStep = 0;

    updateProgress();

    function updateProgress() {
        const progress = ((currentStep + 1) / steps.length) * 100;
        progressBar.style.width = progress + "%";
    }

    function showStep(stepIndex) {
        steps.forEach((step, index) => {
            if (index === stepIndex) {
                step.style.display = "block";
            } else {
                step.style.display = "none";
            }
        });
        updateProgress();
    }

    form.addEventListener("submit", function(event) {
        event.preventDefault();
        // Perform form submission actions here
    });

    form.querySelectorAll(".next-step").forEach(button => {
        button.addEventListener("click", function() {
            currentStep++;
            showStep(currentStep);
        });
    });

    form.querySelectorAll(".prev-step").forEach(button => {
        button.addEventListener("click", function() {
            currentStep--;
            showStep(currentStep);
        });
    });
});

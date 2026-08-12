document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("analysisForm");
    if (!form) return;

    const resumeInput = document.getElementById("resume");
    const dropzone = document.getElementById("dropzone");
    const browseButton = document.getElementById("browseButton");
    const fileName = document.getElementById("fileName");
    const resumeError = document.getElementById("resumeError");
    const jobDescription = document.getElementById("job_description");
    const charCount = document.getElementById("charCount");
    const jdStatus = document.getElementById("jdStatus");
    const jdError = document.getElementById("jdError");
    const submitButton = document.getElementById("submitButton");
    const loadingOverlay = document.getElementById("loadingOverlay");

    const MAX_FILE_SIZE = 5 * 1024 * 1024;
    const MIN_JD_LENGTH = 100;
    const ALLOWED_TYPES = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"];

    const setResumeError = (message = "") => {
        resumeError.textContent = message;
        resumeInput.setAttribute("aria-invalid", message ? "true" : "false");
    };

    const setJdError = (message = "") => {
        jdError.textContent = message;
        jobDescription.setAttribute("aria-invalid", message ? "true" : "false");
    };

    const validateResume = () => {
        const file = resumeInput.files[0];

        if (!file) {
            setResumeError("Please choose a PDF or DOCX resume.");
            return false;
        }

        const extension = file.name.toLowerCase().split(".").pop();
        if (!["pdf", "docx"].includes(extension)) {
            setResumeError("Only PDF and DOCX resumes are supported.");
            return false;
        }

        if (file.size > MAX_FILE_SIZE) {
            setResumeError("This file is larger than the 5 MB limit.");
            return false;
        }

        setResumeError("");
        fileName.textContent = file.name;
        return true;
    };

    const updateJdState = () => {
        const length = jobDescription.value.trim().length;
        charCount.textContent = `${length} / ${MIN_JD_LENGTH} minimum`;

        if (length >= MIN_JD_LENGTH) {
            jdStatus.textContent = "Ready to analyze";
            jdStatus.classList.add("valid");
            jdStatus.classList.remove("invalid");
            setJdError("");
            return true;
        }

        jdStatus.textContent = "Needs more detail";
        jdStatus.classList.add("invalid");
        jdStatus.classList.remove("valid");
        setJdError(`Please enter at least ${MIN_JD_LENGTH} characters.`);
        return false;
    };

    const openFilePicker = () => resumeInput.click();

    browseButton?.addEventListener("click", (event) => {
        event.stopPropagation();
        openFilePicker();
    });

    dropzone?.addEventListener("click", () => openFilePicker());

    dropzone?.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            openFilePicker();
        }
    });

    resumeInput.addEventListener("change", validateResume);
    jobDescription.addEventListener("input", updateJdState);

    ["dragenter", "dragover"].forEach((eventName) => {
        dropzone?.addEventListener(eventName, (event) => {
            event.preventDefault();
            dropzone.classList.add("dragging");
        });
    });

    ["dragleave", "drop"].forEach((eventName) => {
        dropzone?.addEventListener(eventName, (event) => {
            event.preventDefault();
            dropzone.classList.remove("dragging");
        });
    });

    dropzone?.addEventListener("drop", (event) => {
        const files = event.dataTransfer.files;
        if (!files.length) return;

        try {
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(files[0]);
            resumeInput.files = dataTransfer.files;
        } catch {
            setResumeError("Please use the file picker to select your resume.");
            return;
        }

        validateResume();
    });

    form.addEventListener("submit", (event) => {
        const resumeValid = validateResume();
        const jdValid = updateJdState();

        if (!resumeValid || !jdValid) {
            event.preventDefault();

            if (!resumeValid) {
                resumeInput.focus();
            } else {
                jobDescription.focus();
            }
            return;
        }

        submitButton.disabled = true;
        submitButton.classList.add("loading");
        submitButton.querySelector(".button-label").textContent = "Analyzing...";
        loadingOverlay.hidden = false;
        document.body.style.overflow = "hidden";
    });

    updateJdState();
});

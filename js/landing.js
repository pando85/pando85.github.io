/* Landing-only enhancements. No dependency or external service is required. */
document.addEventListener("DOMContentLoaded", () => {
  const mobileMenu = document.querySelector(".mobile-menu");
  if (mobileMenu) {
    mobileMenu.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        mobileMenu.open = false;
      });
    });

    window.addEventListener("hashchange", () => {
      mobileMenu.open = false;
    });

    mobileMenu.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        mobileMenu.open = false;
        mobileMenu.querySelector("summary")?.focus();
      }
    });

    document.addEventListener("click", (event) => {
      if (mobileMenu.open && !mobileMenu.contains(event.target)) {
        mobileMenu.open = false;
      }
    });
  }

  document.querySelectorAll("[data-copy-target]").forEach((button) => {
    button.addEventListener("click", async () => {
      const id = button.getAttribute("data-copy-target");
      const source = document.getElementById(id);
      const feedback = button.closest(".install-card")?.querySelector(".copy-feedback");
      if (!source || !feedback) return;

      try {
        if (!navigator.clipboard?.writeText) {
          throw new Error("Clipboard API unavailable");
        }
        await navigator.clipboard.writeText(source.textContent.trim());
        button.textContent = "Copied";
        button.setAttribute("aria-label", "Helm commands copied");
        feedback.textContent = "Commands copied to clipboard.";
      } catch {
        button.textContent = "Copy";
        feedback.textContent = "Copy is unavailable. Select the commands to copy manually.";
      }
    });
  });
});

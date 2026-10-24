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
  // WAI-ARIA tabs: click and Arrow/Home/End navigation with roving tabindex.
  const tablist = document.querySelector(".code-tabs[role='tablist']");
  if (tablist) {
    const tabs = Array.from(tablist.querySelectorAll("[role='tab']"));
    const filename = document.getElementById("hero-code-filename");
    const docsLink = document.querySelector(".code-doc-link");

    const activateTab = (index, moveFocus = false) => {
      tabs.forEach((tab, i) => {
        const active = i === index;
        tab.setAttribute("aria-selected", String(active));
        tab.tabIndex = active ? 0 : -1;
        const panel = document.getElementById(tab.getAttribute("aria-controls"));
        if (panel) panel.hidden = !active;
      });
      const selected = tabs[index];
      if (filename) filename.textContent = selected.dataset.codeFile;
      if (docsLink) {
        const key = selected.id.slice("tab-".length);
        const target = docsLink.getAttribute("data-code-doc-" + key);
        if (target) docsLink.href = target;
      }
      if (moveFocus) selected.focus();
    };

    tabs.forEach((tab, index) => {
      tab.addEventListener("click", () => activateTab(index));
      tab.addEventListener("keydown", (event) => {
        let next;
        if (event.key === "ArrowRight") next = (index + 1) % tabs.length;
        if (event.key === "ArrowLeft") next = (index + tabs.length - 1) % tabs.length;
        if (event.key === "Home") next = 0;
        if (event.key === "End") next = tabs.length - 1;
        if (next === undefined) return;
        event.preventDefault();
        activateTab(next, true);
      });
    });
  }

});

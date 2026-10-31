// Report toolbar: toggle editing of the numerologist's notes, print, and save a standalone HTML copy.
(function () {
    const scriptEl = document.currentScript;
    const editToggle = document.getElementById('editToggle');
    const editables = () => document.querySelectorAll('.editable');
    let editing = true;

    function setEditing(on) {
        editing = on;
        editables().forEach((el) => el.setAttribute('contenteditable', on ? 'true' : 'false'));
        document.body.classList.toggle('editing-off', !on);
        editToggle.textContent = on ? 'Editing on' : 'Editing off';
        editToggle.setAttribute('aria-pressed', String(on));
    }

    // Inline same-origin stylesheets so the saved file renders without the server.
    async function inlineStylesheets(root) {
        const links = root.querySelectorAll('link[rel="stylesheet"]');
        for (const link of links) {
            const href = link.getAttribute('href') || '';
            if (!href.startsWith('/')) continue;
            try {
                const css = await (await fetch(href)).text();
                const style = document.createElement('style');
                if (link.media) style.media = link.media;
                style.textContent = css;
                link.replaceWith(style);
            } catch (err) {
                console.warn('Could not inline stylesheet', href, err);
            }
        }
    }

    async function saveAsHtml() {
        const wasEditing = editing;
        setEditing(false);

        const copy = document.documentElement.cloneNode(true);
        copy.querySelectorAll('.toolbar, script, .edit-hint').forEach((el) => el.remove());
        copy.querySelectorAll('[contenteditable]').forEach((el) => el.removeAttribute('contenteditable'));
        await inlineStylesheets(copy);

        const blob = new Blob(['<!DOCTYPE html>\n' + copy.outerHTML], { type: 'text/html' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = scriptEl.dataset.filename || 'report.html';
        link.click();
        URL.revokeObjectURL(link.href);

        setEditing(wasEditing);
    }

    editToggle.addEventListener('click', () => setEditing(!editing));
    document.getElementById('saveHtml').addEventListener('click', saveAsHtml);
    document.getElementById('printBtn').addEventListener('click', () => window.print());
    setEditing(true);
})();

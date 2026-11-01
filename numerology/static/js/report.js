/*
 * Report toolbar, shared by the Flask app and the static build.
 *
 * - Full / Client view: the client view hides every element marked .pro-only
 *   (working, tables of calculations, technical data) and is remembered in the
 *   URL (?view=client) so a refresh keeps it.
 * - Editing on/off for the practitioner's notes.
 * - Print, and Save HTML as a standalone file; in the client view the hidden
 *   working is removed from the saved file, not just hidden.
 */
window.initReportToolbar = function (filename, initialView) {
    const editToggle = document.getElementById('editToggle');
    const viewToggle = document.getElementById('viewToggle');
    const editables = () => document.querySelectorAll('.editable');
    let editing = true;
    let clientView = initialView === 'client';

    function setEditing(on) {
        editing = on;
        editables().forEach((el) => el.setAttribute('contenteditable', on ? 'true' : 'false'));
        document.body.classList.toggle('editing-off', !on);
        editToggle.textContent = on ? 'Editing on' : 'Editing off';
        editToggle.setAttribute('aria-pressed', String(on));
    }

    // The view lives in the query string (Flask) or in the hash's query (static build).
    function rememberView() {
        const inHash = location.hash.includes('?');
        const query = inHash ? location.hash.split('?')[1] : location.search.slice(1);
        const params = new URLSearchParams(query);
        if (clientView) params.set('view', 'client'); else params.delete('view');
        const url = inHash
            ? location.pathname + location.search + location.hash.split('?')[0] + '?' + params.toString()
            : location.pathname + (params.toString() ? '?' + params.toString() : '') + location.hash;
        history.replaceState(null, '', url);
    }

    // Re-open this report with some query parameters changed (Flask query string or static-build hash).
    function reopenWith(changes) {
        const inHash = location.hash.startsWith('#/');
        const [path, query] = inHash ? location.hash.split('?') : [location.pathname, location.search.slice(1)];
        const params = new URLSearchParams(query || '');
        Object.entries(changes).forEach(([k, v]) => { if (v) params.set(k, v); else params.delete(k); });
        if (inHash) location.hash = path + '?' + params.toString();
        else location.href = path + '?' + params.toString();
    }

    function setView(client) {
        clientView = client;
        document.body.classList.toggle('client-view', client);
        viewToggle.textContent = client ? 'Client view' : 'Full view';
        viewToggle.setAttribute('aria-pressed', String(client));
        rememberView();
    }

    // Inline same-origin stylesheets so the saved file renders without the server.
    async function inlineStylesheets(root) {
        for (const link of root.querySelectorAll('link[rel="stylesheet"]')) {
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
        copy.querySelectorAll('.toolbar, script, .edit-hint, .aurora, .grain, #dust, .option-form').forEach((el) => el.remove());
        if (clientView) copy.querySelectorAll('.pro-only').forEach((el) => el.remove());
        copy.querySelectorAll('[contenteditable]').forEach((el) => el.removeAttribute('contenteditable'));
        copy.querySelectorAll('.editable:empty').forEach((el) => el.remove());
        await inlineStylesheets(copy);

        const blob = new Blob(['<!DOCTYPE html>\n' + copy.outerHTML], { type: 'text/html' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = (clientView ? 'Client_' : '') + filename;
        link.click();
        URL.revokeObjectURL(link.href);

        setEditing(wasEditing);
    }

    document.querySelectorAll('[data-option-form]').forEach((form) => form.addEventListener('submit', (e) => {
        e.preventDefault();
        reopenWith({ option1: form.elements.option1.value.trim(), option2: form.elements.option2.value.trim() });
    }));
    const styleToggle = document.getElementById('styleToggle');
    if (styleToggle) styleToggle.addEventListener('click', () => reopenWith({ style: styleToggle.dataset.style }));

    editToggle.addEventListener('click', () => setEditing(!editing));
    viewToggle.addEventListener('click', () => setView(!clientView));
    document.getElementById('saveHtml').addEventListener('click', saveAsHtml);
    document.getElementById('printBtn').addEventListener('click', () => window.print());
    setEditing(true);
    setView(clientView);
};

// Flask pages load this script directly with data attributes; the static build calls initReportToolbar itself.
if (document.currentScript && document.currentScript.dataset.filename) {
    window.initReportToolbar(document.currentScript.dataset.filename, document.currentScript.dataset.view || '');
}

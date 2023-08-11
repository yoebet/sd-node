ofetch = window.fetch

window.fetch = function () {
    args = [...arguments]
    if (typeof args[0] == 'string') {
        if (args[0].startsWith('/agent-scheduler/')) {
            args[0] = args[0].substring(1)
        }
    }
    return ofetch(args)
}


setTimeout(function () {
    docs_link = document.querySelector('#footer > div:nth-child(1) > a:nth-child(1)')
    if (docs_link && docs_link.getAttribute('href') === '/docs') {
        docs_link.setAttribute('href', 'docs')
    }
}, 3000)

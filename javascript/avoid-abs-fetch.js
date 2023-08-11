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

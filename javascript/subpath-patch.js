// window.ofetch = window.fetch
//
// window.fetch = function (...args) {
//     if (typeof args[0] === 'string') {
//         if (args[0].startsWith('/agent-scheduler/')) {
//             args[0] = args[0].substring(1)
//         }
//     }
//     return ofetch(args)
// }


setTimeout(function () {
    dl = document.querySelector('#footer > div:nth-child(1) > a:nth-child(1)')
    if (dl && dl.getAttribute('href') === '/docs') {
        dl.setAttribute('href', 'docs')
    }
}, 3000)

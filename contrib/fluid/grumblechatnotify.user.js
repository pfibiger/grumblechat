// ==UserScript==
// @name        Grumble Chat Notify
// @namespace   http://grumblechat.com
// @description Shows a Dock badge whenever a new message appears
// @include     http://grumblechat.com/*
// @author      Greg Knauss <greg@eod.com>
// ==/UserScript==

(function () {

    if (!window.fluid) { return; }

    function update() {
        messages = document.title.match(/\((\d+)\)/);
        window.fluid.dockBadge = messages?messages[1]:'';
        setTimeout(update,1000);
    }

    update();
    
})();

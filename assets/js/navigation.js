(function () {
    'use strict';

    var overlays = Array.prototype.slice.call(document.querySelectorAll('[data-home-overlay]'));
    var triggers = Array.prototype.slice.call(document.querySelectorAll('[data-home-open]'));
    var lastTrigger = null;

    function setTriggerState(name, expanded) {
        triggers.forEach(function (trigger) {
            if (trigger.getAttribute('data-home-open') === name && trigger.hasAttribute('aria-expanded')) {
                trigger.setAttribute('aria-expanded', expanded ? 'true' : 'false');
            }
        });
    }

    function closeAll(restoreFocus) {
        overlays.forEach(function (overlay) {
            overlay.classList.remove('is-open');
            overlay.setAttribute('aria-hidden', 'true');
            setTriggerState(overlay.getAttribute('data-home-overlay'), false);
        });
        document.body.classList.remove('home-overlay-open');
        if (restoreFocus && lastTrigger && document.contains(lastTrigger)) {
            lastTrigger.focus();
        }
    }

    function openOverlay(name, source) {
        closeAll(false);
        var overlay = document.querySelector('[data-home-overlay="' + name + '"]');
        if (!overlay) return;
        lastTrigger = source || lastTrigger;
        overlay.classList.add('is-open');
        overlay.setAttribute('aria-hidden', 'false');
        setTriggerState(name, true);
        document.body.classList.add('home-overlay-open');
        var closeButton = overlay.querySelector('[data-home-close]');
        if (closeButton) {
            window.setTimeout(function () { closeButton.focus(); }, 20);
        }
    }

    triggers.forEach(function (trigger) {
        trigger.addEventListener('click', function () {
            openOverlay(trigger.getAttribute('data-home-open'), trigger);
        });
    });

    document.querySelectorAll('[data-home-close]').forEach(function (button) {
        button.addEventListener('click', function () { closeAll(true); });
    });

    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' && document.body.classList.contains('home-overlay-open')) {
            closeAll(true);
        }
    });
}());

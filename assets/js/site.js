/* site.js — progressive enhancement for the portfolio.
 *
 * Nothing here is required to read the page. The grid renders complete and
 * unfiltered with scripting off; this adds the filter and a reveal.
 */
(function () {
	'use strict';

	var reduced = window.matchMedia('(prefers-reduced-motion: reduce)');

	/* ---------------------------------------------------- reveal on scroll */

	function initReveal() {
		var items = document.querySelectorAll('.reveal');
		if (!items.length || !('IntersectionObserver' in window)) return;

		// Only hide things once we know we can reveal them again.
		document.documentElement.classList.add('reveal-ready');

		var io = new IntersectionObserver(function (entries) {
			entries.forEach(function (entry) {
				if (!entry.isIntersecting) return;
				var el = entry.target;
				// Stagger within a row, capped so a long grid never crawls.
				var i = Number(el.dataset.revealIndex || 0);
				el.style.transitionDelay = Math.min(i * 45, 270) + 'ms';
				el.classList.add('is-in');
				io.unobserve(el);
			});
		}, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });

		Array.prototype.forEach.call(items, function (el, i) {
			el.dataset.revealIndex = i % 6;
			io.observe(el);
		});

		// Failsafe. The reveal works by hiding these elements first, so if the
		// observer never delivers, the page is blank. That is not hypothetical:
		// it happens in headless rendering with no compositor, and it is the
		// kind of thing an extension or an odd engine can also cause. One
		// second after load, check.
		window.addEventListener('load', function () {
			window.setTimeout(function () {
				var revealed = document.querySelectorAll('.reveal.is-in').length;

				// Nothing at all came back: assume the observer is dead and
				// take the animation off the table rather than the content.
				if (!revealed) {
					document.documentElement.classList.remove('reveal-ready');
					return;
				}

				// Otherwise just catch anything on screen that was missed.
				var vh = window.innerHeight;
				Array.prototype.forEach.call(items, function (el) {
					if (el.classList.contains('is-in')) return;
					var box = el.getBoundingClientRect();
					if (box.top < vh && box.bottom > 0) {
						el.classList.add('is-in');
						io.unobserve(el);
					}
				});
			}, 1000);
		});
	}

	/* ---------------------------------------------------------- work filter */

	function initFilter() {
		var grid = document.getElementById('work-grid');
		if (!grid) return;

		var buttons = Array.prototype.slice.call(document.querySelectorAll('.filter'));
		var cards = Array.prototype.slice.call(grid.querySelectorAll('.card'));
		var counter = document.getElementById('work-count');
		var names = buttons.map(function (b) { return b.dataset.filter; });
		var current = null;
		var timer = null;

		function paint(filter) {
			var shown = 0;

			buttons.forEach(function (b) {
				var on = b.dataset.filter === filter;
				b.setAttribute('aria-pressed', on ? 'true' : 'false');
			});

			cards.forEach(function (card) {
				var match = filter === 'all' || card.dataset.kind === filter;
				card.classList.toggle('is-hidden', !match);
				if (match) shown++;
			});

			if (counter) {
				counter.textContent = filter === 'all'
					? shown + ' projects'
					: shown + ' of ' + cards.length;
			}
		}

		function apply(filter, animate) {
			if (names.indexOf(filter) === -1) filter = 'all';
			if (filter === current) return;
			current = filter;

			// Dip the grid, swap, bring it back. Filtering changes which
			// items exist, so there is no shared element to move between
			// states — a crossfade is the honest transition, and it hides
			// the reflow.
			if (!animate || reduced.matches) { paint(filter); return; }

			window.clearTimeout(timer);
			grid.classList.add('is-swapping');
			timer = window.setTimeout(function () {
				paint(filter);
				// Next frame, so the browser paints the swapped state at
				// opacity 0 before the transition back begins.
				requestAnimationFrame(function () {
					grid.classList.remove('is-swapping');
				});
			}, 130);
		}

		function fromHash() {
			return (location.hash || '').replace(/^#/, '');
		}

		buttons.forEach(function (button) {
			button.addEventListener('click', function () {
				var filter = this.dataset.filter;
				apply(filter, true);
				// replaceState, not pushState: filtering is not a navigation
				// step, so it should not fill the back button with clicks.
				var url = filter === 'all'
					? location.pathname + location.search
					: '#' + filter;
				if (history.replaceState) history.replaceState(null, '', url);
			});
		});

		window.addEventListener('hashchange', function () { apply(fromHash(), true); });

		apply(fromHash(), false);
	}

	function init() {
		initReveal();
		initFilter();
	}

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', init);
	} else {
		init();
	}
})();

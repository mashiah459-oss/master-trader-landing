/*
 * Meta pixel + funnel events, shared by every page in the funnel.
 *
 * Include it in <head>, followed by the <noscript> fallback image
 * (a <noscript> can only live in the HTML, script never runs without JS):
 *
 *   <script src="js/pixel.js"></script>
 *   <noscript><img height="1" width="1" style="display:none"
 *     src="https://www.facebook.com/tr?id=3092602027607133&ev=PageView&noscript=1"/></noscript>
 *
 * Pages that already carry the inline pixel snippet (club, quiz, workshop,
 * community, thankyou, shachaf) keep it: loadPixel() sees window.fbq and skips
 * its own init, so nothing is ever initialised twice.
 */
(function (window, document) {
  'use strict';

  var PIXEL_ID = '3092602027607133';
  var CURRENCY = 'ILS';

  function loadPixel() {
    if (window.fbq) return;
    /* eslint-disable */
    !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
    n.callMethod.apply(n,arguments):n.queue.push(arguments)};
    if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];
    t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];
    s.parentNode.insertBefore(t,s)}(window,document,'script',
    'https://connect.facebook.net/en_US/fbevents.js');
    /* eslint-enable */
    window.fbq('init', PIXEL_ID);
    window.fbq('track', 'PageView');
  }

  // One id per event, sent to Meta and to the lead endpoint, so the same lead
  // arriving twice (browser + server) is counted once.
  function eventId(prefix) {
    return (prefix || 'EV') + '_' + Date.now() + '_' + Math.floor(Math.random() * 1e6);
  }

  function trackLead(contentName, prefix) {
    var id = eventId(prefix || 'L');
    if (window.fbq) {
      window.fbq('track', 'Lead', contentName ? { content_name: contentName } : {}, { eventID: id });
    }
    return id;
  }

  // A missing or malformed value still fires the event, without value/currency:
  // an untagged InitiateCheckout is worth far more than no event at all.
  function trackCheckout(value) {
    if (!window.fbq) return;
    var params = {};
    if (typeof value === 'number' && isFinite(value)) {
      params.value = value;
      params.currency = CURRENCY;
    }
    window.fbq('track', 'InitiateCheckout', params);
  }

  // Meta appends fbclid to every ad click, which separates paid from organic
  // without editing any creative, so no winning ad has its learning reset.
  function whopUrl(base, campaign) {
    var p = new URLSearchParams(window.location.search);
    var fromAd = p.has('fbclid') || p.get('utm_source') === 'meta';
    var out = new URLSearchParams();
    out.set('utm_source', fromAd ? 'meta' : (p.get('utm_source') || 'organic'));
    out.set('utm_medium', fromAd ? 'paid' : (p.get('utm_medium') || 'web'));
    out.set('utm_campaign', p.get('utm_campaign') || campaign || 'site');
    var content = p.get('utm_content') || p.get('ad') || '';
    if (content) out.set('utm_content', content);
    if (p.get('fbclid')) out.set('fbclid', p.get('fbclid'));
    return base + (base.indexOf('?') === -1 ? '?' : '&') + out.toString();
  }

  // Points every Whop link on the page at the tagged URL and fires
  // InitiateCheckout when one is clicked.
  function wireWhopLinks(options) {
    var opts = options || {};
    var selector = opts.selector || 'a[href^="https://whop.com/"]';
    var links = document.querySelectorAll(selector);
    Array.prototype.forEach.call(links, function (link) {
      var href = link.getAttribute('href');
      if (!href) return;
      var base = href.split('?')[0];
      link.href = whopUrl(base, opts.campaign);
      link.addEventListener('click', function () { trackCheckout(opts.value); });
    });
    return links.length;
  }

  loadPixel();

  window.mtPixel = {
    id: PIXEL_ID,
    eventId: eventId,
    trackLead: trackLead,
    trackCheckout: trackCheckout,
    whopUrl: whopUrl,
    wireWhopLinks: wireWhopLinks
  };
})(window, document);

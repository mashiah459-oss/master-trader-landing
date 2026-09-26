/*
 * campaigns.js — המקור היחיד לכל מה שנמכר באתר.
 *
 * כל מוצר מופיע פה פעם אחת: סטטוס, מחיר, תאריכים, כתובת הדף וקישור התשלום.
 * דף שמחובר לקובץ הזה מושך ממנו את התגית, את הטקסט של הכפתור ואת הקישור,
 * כך שמחזור חדש או שינוי מחיר הם עריכה אחת כאן ולא חיפוש בכמה דפים.
 *
 * ── איך מעדכנים ──────────────────────────────────────────────
 * לסגור מחזור:        status: 'closed'   → האריח של המוצר נעלם מדף המוצרים
 * לפתוח רשימת המתנה:  status: 'waitlist' → התגית הופכת ל״המועד הבא יפורסם״
 * לפתוח מכירה:        status: 'open'
 * לשנות מחיר:         price: 149         (המספר בשקלים, בלי סימן ₪)
 * מחזור חדש:          לעדכן cycle, opens ואת רשימת dates
 *
 * ── חשוב ─────────────────────────────────────────────────────
 * הטקסט שכתוב ב-HTML הוא ברירת המחדל. אם הקובץ הזה לא נטען, הדף ממשיך
 * להיראות בדיוק כמו קודם, ולכן אסור למחוק את הטקסט מה-HTML.
 * תאריכים נכתבים כמו שהם מוצגים לגולש: '18.10'.
 */
(function (window, document) {
  'use strict';

  var CAMPAIGNS = {
    club: {
      name: 'מועדון הסוחר המתמיד',
      status: 'open',
      price: 149,
      priceNote: 'לחודש',
      url: 'club.html',
      checkout: 'https://whop.com/master-trader-club/',
      tag: 'מנוי חודשי',
      cta: 'להצטרפות למועדון'
    },

    situationRoom: {
      name: 'חדר מצב',
      status: 'open',
      cycle: 2,
      opens: '18.10',
      dates: ['18.10', '08.11', '15.11', '29.11', '20.12'],
      seats: 20,
      price: null,              // אין מחיר בדף חדר המצב, ולכן אין מחיר כאן
      url: 'hadar-hamatzav/',
      checkout: null,           // ההרשמה היא דרך הטופס בדף עצמו
      tag: null,                // התגית נבנית לבד: "מחזור 2 · נפתח 18.10"
      cta: 'לפרטים והרשמה'
    },

    course: {
      name: 'עסק או עסקה',
      status: 'open',
      price: 297,
      fullPrice: 387,
      url: 'course.html',
      checkout: 'https://whop.com/trading-as-a-business/58c43258-c998-4f1d-a2db-6707625723a3/',
      tag: 'קורס דיגיטלי',
      cta: 'לפרטים על הקורס'
    },

    personalSession: {
      name: 'פגישה אישית',
      status: 'open',
      price: 888,
      url: 'apply.html',
      checkout: null,           // מגישים מועמדות, ומתן חוזר לתאם
      tag: 'אחד על אחד',
      cta: 'להגשת מועמדות'
    },

    workshop: {
      name: 'סדנת תורת הרבעים',
      status: 'waitlist',
      date: null,               // המועד הבא טרם נקבע
      seats: 30,
      price: null,
      url: 'workshop.html#waitlist',
      checkout: null,
      tag: null,                // בסטטוס רשימת המתנה התגית נבנית לבד
      cta: 'לרשימת ההמתנה'
    }
  };

  // התגית שמופיעה בפינת האריח. נבנית מהנתונים, כדי שמחזור חדש יתעדכן מעצמו.
  function tagFor(product) {
    if (!product) return '';
    if (product.status === 'waitlist') return 'המועד הבא יפורסם';
    if (product.cycle && product.opens) {
      return 'מחזור ' + product.cycle + ' · נפתח ' + product.opens;
    }
    if (product.date) return 'המועד הבא · ' + product.date;
    return product.tag || '';
  }

  // מחליף רק את הטקסט של האריח, ומשאיר את החץ ואת שאר המבנה במקום.
  function setLabel(element, text) {
    if (!element || !text) return;
    var first = element.firstChild;
    if (first && first.nodeType === 3) {
      first.nodeValue = text;
      return;
    }
    element.insertBefore(document.createTextNode(text), first || null);
  }

  // כל אריח מסומן ב-HTML ב-data-campaign עם שם המוצר מהרשימה שלמעלה.
  function apply() {
    var tiles = document.querySelectorAll('[data-campaign]');
    Array.prototype.forEach.call(tiles, function (tile) {
      var product = CAMPAIGNS[tile.getAttribute('data-campaign')];
      if (!product) return;                    // שם לא מוכר: משאירים את ה-HTML כמו שהוא

      if (product.status === 'closed') {       // מוצר סגור לא מוצג בכלל
        tile.remove();
        return;
      }

      if (product.url && tile.tagName === 'A') tile.href = product.url;

      // תגית ריקה לא נכתבת: עדיף להשאיר את מה שכתוב ב-HTML מאשר למחוק אותו.
      var tag = tile.querySelector('[data-campaign-tag]') || tile.querySelector('.tag');
      var tagText = tagFor(product);
      if (tag && tagText) tag.textContent = tagText;

      var cta = tile.querySelector('[data-campaign-cta]') || tile.querySelector('.go');
      setLabel(cta, product.cta);
    });
  }

  window.CAMPAIGNS = CAMPAIGNS;
  window.campaignTag = tagFor;
  window.applyCampaigns = apply;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', apply);
  } else {
    apply();
  }
})(window, document);

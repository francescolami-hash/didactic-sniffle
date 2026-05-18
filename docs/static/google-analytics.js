/*
 * Google Analytics 4
 *
 * GA4 Measurement ID for this website.
 * Google Analytics: Admin > Data streams > Web > Measurement ID.
 */
(function () {
    const GA_MEASUREMENT_ID = "G-L6NFTJG21D";

    if (!GA_MEASUREMENT_ID || GA_MEASUREMENT_ID === "G-XXXXXXXXXX") {
        return;
    }

    window.dataLayer = window.dataLayer || [];

    function gtag() {
        window.dataLayer.push(arguments);
    }

    window.gtag = gtag;
    gtag("js", new Date());
    gtag("config", GA_MEASUREMENT_ID);

    const script = document.createElement("script");
    script.async = true;
    script.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(GA_MEASUREMENT_ID);
    document.head.appendChild(script);
})();

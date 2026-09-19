$urls = @(
    '/', '/about', '/blog', '/blog_details', '/class_details', '/class_timetable',
    '/contact', '/gallery', '/team', '/services', '/dashboard/', '/bmi_calculator',
    '/chatbot/', '/member-progress/', '/payment-dashboard/', '/testimonials/',
    '/reports/', '/nonexistent-page-xyz/'
)
foreach ($u in $urls) {
    try {
        $r = Invoke-WebRequest -Uri "http://127.0.0.1:8017$u" -UseBasicParsing -TimeoutSec 30 -ErrorAction Stop
        Write-Host "$($r.StatusCode)  $u"
    } catch {
        $code = $_.Exception.Response.StatusCode.value__
        Write-Host "$code  $u"
    }
}

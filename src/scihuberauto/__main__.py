import asyncio
from random import uniform
from playwright.async_api import async_playwright, Page, Download

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 GLS/100.10.9939.100"

NUMBER = "269428801644"
PASSWD = "284659"


async def scroll_search_result(page: Page):
    
    await page.keyboard.press("ArrowDown")


async def try_ignore_cookies(page: Page):
    cookies_loc = page.locator(
        ".onetrust-close-btn-handler.onetrust-close-btn-ui.banner-close-button.ot-close-icon"
    )

    await asyncio.sleep(uniform(3.0, 5.0))

    cookies = await cookies_loc.all()
    if cookies:
        await cookies[0].click()


async def login_wos(page: Page):
    await page.goto("http://www.scihuber.com/e/member/login/")
    username_loc = page.locator("input#password[name='username']")
    password_loc = page.locator("input#username[name='password']")
    login_loc = page.locator("input[name='Submit']")

    await username_loc.fill(NUMBER)
    await password_loc.fill(PASSWD)
    await login_loc.click()

    await asyncio.sleep(uniform(3.0, 5.0))
    await page.goto("http://www.scihuber.com/e/action/ShowInfo.php?classid=186&id=3251")
    await asyncio.sleep(uniform(1.5, 3.0))


async def advanced_search(year: int, page: Page):
    expr = f"(SO=(INTERNATIONAL JOURNAL OF INFORMATION MANAGEMENT)) AND (DT=(Article)) AND (DOP=({year})) NOT (OO=(China))"
    await page.goto("https://webofscience.clarivate.cn/wos/alldb/advanced-search")
    expr_loc = page.locator("textarea#advancedSearchInputArea")
    search_loc = page.locator("button[data-ta=run-search]")

    await try_ignore_cookies(page)
    await expr_loc.fill(expr)
    await search_loc.click()


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(user_agent=USER_AGENT)

        async def page_save_file(p: Page):
            async def save_file(d: Download):
                print(d.suggested_filename)

            p.on("download", save_file)

        context.on("page", page_save_file)
        page = await context.new_page()

        await login_wos(page)

        await advanced_search(2014, page)
        await asyncio.sleep(5)
        await scroll_search_result(page)

        citation_loc = page.locator("a[data-ta='stat-number-citation-related-count']")
        for citation in await citation_loc.all():
            url = await citation.get_attribute("href")
            print(url)
        await asyncio.sleep(1000)

        await page.close()
        await context.close()


if __name__ == "__main__":
    asyncio.run(main())

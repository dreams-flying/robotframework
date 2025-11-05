from playwright.sync_api import Playwright, sync_playwright
import re

def execute_automation(
    playwright: Playwright,
    url: str = "https://h5-office.bestpay.com.cn/sec-iam-plus-h5/index.html#/portal/list",
    appcause: str = "参加学术会议",
    cost: str = "3500",
    staydays: str = "3"
) -> None:
    """
    自动化执行函数 - 从Playwright Codegen转换

    参数:
        playwright: Playwright实例
        url: 访问的URL
        appcause: appcause字段的值（默认: 参加学术会议）
        cost: cost字段的值（默认: 3500）
        staydays: staydays字段的值（默认: 3）
    """
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # 导航到页面
    page.goto(url)

    page.goto("https://h5-office.bestpay.com.cn/sec-iam-plus-h5/index.html#/portal/list")
    # Popup操作: page1
    with page.expect_popup() as page1_info:
        page.get_by_text("OA系统").first.click()
    page1 = page1_info.value

    # Popup操作: page2
    with page1.expect_popup() as page2_info:
        page1.locator("#magnet_8490099577463589529").get_by_title("人力系统").locator("span").click()
    page2 = page2_info.value

    page2.get_by_role("tab", name="员工自助").click()
    page2.get_by_role("link", name="员工出差申请单-新").click()
    page2.get_by_role("row", name="出差类型").get_by_label("").click()
    page2.get_by_role("option", name="外地出差").click()
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.SDATE").get_by_placeholder("YYYYMMDD").click()
    page2.get_by_role("cell", name="5", exact=True).first.click()
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.STIME").get_by_label("").click()
    page2.get_by_role("option", name="08:30").click()
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.EDATE").get_by_placeholder("YYYYMMDD").click()
    page2.get_by_role("cell", name="7", exact=True).click()
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.ETIME").get_by_label("").click()
    page2.get_by_role("option", name="17:30").click()
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.APPCAUSE").get_by_role("textbox").click()
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.APPCAUSE").get_by_role("textbox").fill(appcause)
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.COST").get_by_role("textbox").click()
    page2.get_by_role("cell", name="WF_ATS_LEAVEINFO.COST").get_by_role("textbox").fill(cost)
    page2.get_by_role("textbox", name="否").click()
    page2.get_by_role("option", name="否").click()
    page2.get_by_role("button", name="了解").click()
    page2.get_by_role("cell", name="WF_ATS_TRAVLE.FROMCITY").get_by_role("textbox").click()
    page2.get_by_role("list").filter(has_text="上海上海").locator("span").click()
    page2.get_by_role("radio", name="上海").check()
    page2.get_by_role("cell", name="WF_ATS_TRAVLE.TOCITY").get_by_role("textbox").click()
    page2.get_by_role("list").filter(has_text="北京北京").locator("span").click()
    page2.get_by_role("radio", name="北京").check()
    page2.get_by_role("cell", name="WF_ATS_TRAVLE.VEHICLE1").get_by_label("").click()
    page2.get_by_role("option", name="飞机").click()
    page2.get_by_role("cell", name="WF_ATS_TRAVLE.ISSTAY").get_by_label("").click()
    page2.get_by_role("option", name="是").click()
    page2.get_by_role("cell", name="WF_ATS_TRAVLE.STAYDAYS").get_by_role("textbox").click()
    page2.get_by_role("cell", name="WF_ATS_TRAVLE.STAYDAYS").get_by_role("textbox").fill(staydays)
    page2.get_by_role("cell", name="WF_ATS_TRAVLE.BZ_COMP").get_by_role("textbox").click()
    page2.get_by_role("radio", name="天翼支付科技有限公司（本部）").check()
    page2.get_by_role("cell", name="WF_ATS_TRAVLE.BZ_REIMBU").get_by_role("textbox").click()
    page2.get_by_role("listitem").filter(has_text="天翼支付科技有限公司（本部）").locator("span").click()
    page2.get_by_role("listitem").filter(has_text=re.compile(r"^技术与大数据平台部$")).locator("span").click()
    page2.get_by_text("技术与大数据平台部").nth(1).click()
    page2.get_by_role("cell", name="WF_ATS_TRAVLE.PRODUCTA").get_by_label("").click()
    page2.get_by_role("option", name="全产品线摊销").click()
    page2.get_by_role("row", name="是否为研发事项出差 研发项目名称").get_by_label("").click()
    page2.get_by_role("option", name="是").click()
    page2.get_by_role("cell", name="WF_ATS_TRAVLE.RDPROJECT").get_by_role("textbox").click()
    page2.get_by_text("年中国电信天翼电子商务有限公司线下支付能力研发项目").click()
    page2.wait_for_timeout(5000)
    run(playwright)

    # 清理
    context.close()
    browser.close()
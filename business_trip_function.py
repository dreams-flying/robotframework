from playwright.sync_api import Playwright, sync_playwright

def execute_automation(
    playwright: Playwright,
    url: str = "https://h5-office.bestpay.com.cn/sec-iam-plus-h5/index.html#/portal/list",
    stime: str = "08:30",
    etime: str = "17:30",
    appcause: str = "参加学术会议",
    cost: str = "否",
    fromcity: str = "上海",
    tocity: str = "北京",
    vehicle1: str = "飞机",
    isstay: str = "是",
    staydays: str = "3",
    bz_comp: str = "天翼支付科技有限公司（本部）",
    producta: str = "是"
) -> None:
    """
    自动生成的自动化函数

    参数:
        playwright: Playwright实例
        url: 访问URL
        stime: STIME字段的值
        etime: ETIME字段的值
        appcause: APPCAUSE字段的值
        cost: COST字段的值
        fromcity: FROMCITY字段的值
        tocity: TOCITY字段的值
        vehicle1: VEHICLE1字段的值
        isstay: ISSTAY字段的值
        staydays: STAYDAYS字段的值
        bz_comp: BZ_COMP字段的值
        producta: PRODUCTA字段的值
    """
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # 导航到页面
    page.goto(url)

    # 执行操作序列
    # EXPECT_POPUP 操作
    page.get_by_role('unknown', name='').expect_popup()
    # CLICK 操作
    page.get_by_text('OA系统').first.click()
    # EXPECT_POPUP 操作
    page.get_by_role('unknown', name='').expect_popup()
    # CLICK 操作
    page.locator('#magnet_8490099577463589529').locator('span').click()
    page1.get_by_role('tab', name='员工自助').click()
    page1.get_by_role('link', name='员工出差申请单-新').click()
    page1.get_by_role('row', name='出差类型').click()
    page1.get_by_role('option', name='外地出差').click()
    page1.get_by_role('cell', name='WF_ATS_LEAVEINFO.SDATE').get_by_placeholder('YYYYMMDD').click()
    page1.get_by_role('cell').first.click()
    page1.get_by_role('cell', name='WF_ATS_LEAVEINFO.STIME').click()
    page1.get_by_role('option', name='08:30').click()
    page1.get_by_role('cell', name='WF_ATS_LEAVEINFO.EDATE').get_by_placeholder('YYYYMMDD').click()
    page1.get_by_role('cell').click()
    page1.get_by_role('cell', name='WF_ATS_LEAVEINFO.ETIME').click()
    page1.get_by_role('option', name='17:30').click()
    page1.get_by_role('cell', name='WF_ATS_LEAVEINFO.APPCAUSE').get_by_role('textbox').click()
    # FILL 操作
    page1.get_by_role('cell', name='WF_ATS_LEAVEINFO.APPCAUSE').get_by_role('textbox').fill(appcause)
    # CLICK 操作
    page1.get_by_role('cell', name='WF_ATS_LEAVEINFO.COST').get_by_role('textbox').click()
    # FILL 操作
    page2.get_by_role('cell', name='WF_ATS_LEAVEINFO.COST').get_by_role('textbox').fill(cost)
    # CLICK 操作
    page2.get_by_role('textbox', name='否').click()
    page2.get_by_role('option', name='否').click()
    page2.get_by_role('button', name='了解').click()
    page2.get_by_role('cell', name='WF_ATS_TRAVLE.FROMCITY').get_by_role('textbox').click()
    page2.locator('span').get_by_role('list').filter(has_text='上海上海').click()
    # CHECK 操作
    page2.get_by_role('radio', name='上海').check()
    # CLICK 操作
    page2.get_by_role('cell', name='WF_ATS_TRAVLE.TOCITY').get_by_role('textbox').click()
    page2.locator('span').get_by_role('list').filter(has_text='北京北京').click()
    # CHECK 操作
    page2.get_by_role('radio', name='北京').check()
    # CLICK 操作
    page2.get_by_role('cell', name='WF_ATS_TRAVLE.VEHICLE1').click()
    page2.get_by_role('option', name='飞机').click()
    page2.get_by_role('cell', name='WF_ATS_TRAVLE.ISSTAY').click()
    page2.get_by_role('option', name='是').click()
    page2.get_by_role('cell', name='WF_ATS_TRAVLE.STAYDAYS').get_by_role('textbox').click()
    # FILL 操作
    page2.get_by_role('cell', name='WF_ATS_TRAVLE.STAYDAYS').get_by_role('textbox').fill(staydays)
    # CLICK 操作
    page2.get_by_role('cell', name='WF_ATS_TRAVLE.BZ_COMP').get_by_role('textbox').click()
    # CHECK 操作
    page2.get_by_role('radio', name='天翼支付科技有限公司（本部）').check()
    # CLICK 操作
    page2.get_by_role('cell', name='WF_ATS_TRAVLE.BZ_REIMBU').get_by_role('textbox').click()
    page2.locator('span').get_by_role('listitem').filter(has_text='天翼支付科技有限公司（本部）').click()
    page2.locator('span').get_by_role('listitem').click()
    page2.nth(1).nth(1).click()
    page2.get_by_role('cell', name='WF_ATS_TRAVLE.PRODUCTA').click()
    page2.get_by_role('option', name='全产品线摊销').click()
    page2.get_by_role('row', name='是否为研发事项出差 研发项目名称').click()
    page2.get_by_role('option', name='是').click()
    page2.get_by_role('cell', name='WF_ATS_TRAVLE.RDPROJECT').get_by_role('textbox').click()
    page2.get_by_role('unknown', name='').click()
    # WAIT_TIMEOUT 操作
    page2.get_by_role('unknown', name='').wait_timeout()
    page.wait_for_timeout(5000)

    # 清理
    context.close()
    browser.close()

# 使用示例:
# with sync_playwright() as playwright:
#     execute_automation(playwright)

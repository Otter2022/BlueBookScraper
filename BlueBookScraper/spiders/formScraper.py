import scrapy
from scrapy.utils.response import open_in_browser
import csv
from BlueBookScraper.items import BluebookscraperItem

class FormscraperSpider(scrapy.Spider):
    name = "formScraper"
    custom_settings = {
        'DOWNLOAD_TIMEOUT': 300
    }
    allowed_domains = ["bluebook.utsa.edu"]
    start_urls = ["https://bluebook.utsa.edu/"]

    def fillOutForm(self, response):
        __EVENTTARGET = response.meta['__EVENTTARGET']
        course_id = response.meta['course_id']
        current_page = response.meta['current_page']
        total_pages = response.meta['total_pages']
        #open_in_browser(response)
        __VIEWSTATE = response.css("input#__VIEWSTATE::attr(value)").get()
        __EVENTVALIDATION = response.css("input#__EVENTVALIDATION::attr(value)").get()
        if __EVENTTARGET == "ctl00$MainContentSearchQuery$searchCriteriaEntry$SearchBtn":
            formdata = {
                'ctl00_ToolkitScriptManager1_HiddenField': '',
                  '__EVENTTARGET': __EVENTTARGET,
                # '__EVENTARGUMENT': '',
                # "__VIEWSTATE": __VIEWSTATE,
                # '__VIEWSTATEGENERATOR': 'CA0B0334',
                # '__EVENTVALIDATION': __EVENTVALIDATION,
                'ctl00$MainContentSearchQuery$searchCriteriaEntry$SearchTypeRBL': 'SUBJECT',
                'ctl00$MainContentSearchQuery$searchCriteriaEntry$FacultyTitleTxtBox': '',
                'ctl00$MainContentSearchQuery$searchCriteriaEntry$KeywordTxtBox': '',
                'ctl00$MainContentSearchQuery$searchCriteriaEntry$CourseSubjectCombo$TextBox': 'African American Studies (AAS)',
                'ctl00$MainContentSearchQuery$searchCriteriaEntry$CourseSubjectCombo$HiddenField': str(course_id),
                'ctl00$MainContentSearchQuery$searchCriteriaEntry$AcademicDeptTitleCombo$TextBox': '',
                'ctl00$MainContentSearchQuery$searchCriteriaEntry$AcademicDeptTitleCombo$HiddenField': str(0),
                'ctl00$MainContent$mainContent1$TotalPages': str(total_pages),
                'ctl00$MainContent$mainContent1$TotalRows': str(0),
                'ctl00$MainContent$mainContent1$CurrentPage': str(current_page),
            }
        else:
            formdata = {
                'ctl00_ToolkitScriptManager1_HiddenField': '',
                '__EVENTTARGET': __EVENTTARGET,
                # '__EVENTARGUMENT': '',
                # "__VIEWSTATE": __VIEWSTATE,
                # '__VIEWSTATEGENERATOR': 'CA0B0334',
                # '__EVENTVALIDATION': __EVENTVALIDATION,
                'ctl00$MainContentSearchQuery$searchCriteriaEntry$SearchTypeRBL': 'SUBJECT',
                'ctl00$MainContentSearchQuery$searchCriteriaEntry$FacultyTitleTxtBox': '',
                'ctl00$MainContentSearchQuery$searchCriteriaEntry$KeywordTxtBox': '',
                'ctl00$MainContentSearchQuery$searchCriteriaEntry$CourseSubjectCombo$TextBox': '',
                'ctl00$MainContentSearchQuery$searchCriteriaEntry$CourseSubjectCombo$HiddenField': str(course_id),
                'ctl00$MainContentSearchQuery$searchCriteriaEntry$AcademicDeptTitleCombo$TextBox': 'African American Studies (AAS)',
                'ctl00$MainContentSearchQuery$searchCriteriaEntry$AcademicDeptTitleCombo$HiddenField': str(0),
                'ctl00$MainContent$mainContent1$TotalPages': str(total_pages),
                'ctl00$MainContent$mainContent1$TotalRows': str(30),
                'ctl00$MainContent$mainContent1$CurrentPage': str(current_page),
                'ctl00$MainContent$mainContent1$CourseTermSelectRBL': 'ALL',
                'ctl00$MainContent$mainContent1$MainContentAccordion_AccordionExtender_ClientState': str(-1)
            }
        #print(formdata)
        # print(__EVENTVALIDATION)
        # print(__EVENTTARGET)
        # print(response.url)
        if __EVENTTARGET == 'ctl00$MainContentSearchQuery$searchCriteriaEntry$SearchBtn':
            print('selecting all content')
            # total_pages = response.css('input#ctl00_MainContent_mainContent1_TotalPages::attr(value)').get()
            # print(total_pages)
            yield scrapy.FormRequest.from_response(response, callback=self.fillOutForm, formdata=formdata, formxpath='/html/body/form',
                                                   meta={
                                                       '__EVENTTARGET': 'ctl00$MainContent$mainContent1$CourseTermSelectRBL$1',
                                                       'course_id': course_id, 'current_page': 0, 'total_pages': 1})
        elif __EVENTTARGET == 'ctl00$MainContent$mainContent1$CourseTermSelectRBL$1':
            yield scrapy.FormRequest.from_response(response, callback=self.fillOutForm, formdata=formdata, formxpath='/html/body/form',
                                                   meta={
                                                       '__EVENTTARGET': 'ctl00$MainContent$mainContent1$PagerImgBtn_NextTOP',
                                                       'course_id': course_id, 'current_page': 0,
                                                       'total_pages': 1})

        elif __EVENTTARGET == 'ctl00$MainContent$mainContent1$PagerImgBtn_NextTOP':
            try:
                total_pages = response.css('input#ctl00_MainContent_mainContent1_TotalPages::attr(value)').get()
            except AttributeError:
                total_pages = 0
            for page in range(int(total_pages)):
                # print('page')
                # print("got to pages!")
                formdata['ctl00$MainContent$mainContent1$CurrentPage'] = str(page)
                #open_in_browser(response)
                #print(formdata)
                yield scrapy.FormRequest.from_response(response, callback=self.find_course_info, formdata=formdata, formxpath='/html/body/form', meta={
                                                           '__EVENTTARGET': 'ctl00$MainContent$mainContent1$PagerImgBtn_NextTOP',
                                                           'course_id': course_id, 'current_page': page,
                                                           'total_pages': total_pages})

    def find_course_info(self, response):
        __EVENTTARGET = response.meta['__EVENTTARGET']
        course_id = response.meta['course_id']
        current_page = response.meta['current_page']
        total_pages = response.meta['total_pages']
        # print('page')
        # print('finding courses')
        for index, course in enumerate(response.css("table.infoTable")):
            semester = course.css(f"span#ctl00_MainContent_mainContent1_MainContentAccordion_Pane_{index}_header_SemYrLbl::text").get()
            crn = course.css(f"span#ctl00_MainContent_mainContent1_MainContentAccordion_Pane_{index}_header_crnlbl::text").get()
            courseLabel = course.css(f'span#ctl00_MainContent_mainContent1_MainContentAccordion_Pane_{index}_header_CourseLbl')
            courseLabel = courseLabel.xpath("..")
            courseLabel = ''.join(courseLabel.css('::text').getall()[1:])
            courseTitle = course.css(f"a#ctl00_MainContent_mainContent1_MainContentAccordion_Pane_{index}_header_TitleLnkBtn::text").get()
            instructor = course.css(f"a#ctl00_MainContent_mainContent1_MainContentAccordion_Pane_{index}_header_InstructorLnkBtn::text").get()
            insEval = course.css(f"span#ctl00_MainContent_mainContent1_MainContentAccordion_Pane_{index}_header_InstEval")
            insEval = insEval.xpath("..")
            insEval = ''.join(insEval.css('::text').getall())
            crEval = course.css(f"span#ctl00_MainContent_mainContent1_MainContentAccordion_Pane_{index}_header_CourseEval")
            crEval = crEval.xpath("..")
            crEval = ''.join(crEval.css('::text').getall())
            insEvalData = insEval.split('\n')
            leftPane = response.css(f"div#ctl00_MainContent_mainContent1_MainContentAccordion_Pane_{index}_content_pnlCourseDetailTopLeft::text").getall()
            rightPane = response.css(f"div#ctl00_MainContent_mainContent1_MainContentAccordion_Pane_{index}_content_pnlCourseDetailTopRight::text").getall()
            descriptionPane = response.css(f"div#ctl00_MainContent_mainContent1_MainContentAccordion_Pane_{index}_content_pnlCourseDetailBottom::text").getall()
            bothPanes = leftPane + rightPane
            if not leftPane:
                bothPanes = response.css(f"div#ctl00_MainContent_mainContent1_MainContentAccordion_Pane_{index}_content_pnlSurveyedCourseDetailTopLeft::text").getall()
                enrollment = bothPanes[11].replace('\n','').replace('\r','').strip()
            else:
                enrollment = bothPanes[9].replace('\n', '').replace('\r', '').strip().split('/')[0]
            if not descriptionPane:
                descriptionPane = response.css(f"div#ctl00_MainContent_mainContent1_MainContentAccordion_Pane_{index}_content_pnlSurveyedCourseDetailBottom::text").getall()
            # if not descriptionPane:
            #     print('################################################################')
            #     print(descriptionPane)
            #     open_in_browser(response)
            #     print('################################################################')
            descriptionPane = descriptionPane[1].replace('\n', '').replace('\t', '').replace('\r', '').strip()
            crEvalData = crEval.split('\n')

            # print(bothPanes)
            # print(descriptionPane)
            # if not rightPane:
            #     open_in_browser(response)
            try:
                if "n/a" in insEvalData:
                    insEvalRating = 'n/a'
                    insEvalStudentCnt = 'n/a'
                else:
                    insEvalRating = str(
                        round(float(insEvalData[2].lstrip().replace('\r','').split(' ')[0]) / float(insEvalData[2].lstrip().replace('\r','').split(' ')[2]), 2))
                    insEvalStudentCnt = (insEvalData[3].lstrip().split(" ")[0])
            except ValueError:
                print('valueerror')
                insEvalRating = 'n/a'
                insEvalStudentCnt = 'n/a'
            try:
                if "n/a" in crEvalData:
                    crEvalRating = 'n/a'
                    crEvalStudentCnt = 'n/a'
                else:
                    crEvalRating = str(
                        round((float(crEvalData[2].lstrip().replace('\r','').split(' ')[0]) / float(crEvalData[2].lstrip().replace('\r','').split(' ')[2])), 2))
                    crEvalStudentCnt = (crEvalData[3].lstrip().split(" ")[0])
            except ValueError:
                crEvalRating = 'n/a'
                crEvalStudentCnt = 'n/a'
            # print("got to courses!")
            # print(current_page)
            # print(total_pages)
            with open('test2.csv', 'a', newline='') as csvfile:
                fieldNames = ['crn', 'semester', 'courseLabel', 'instructor', 'courseTitle', 'insEval',
                              'insEvalStudentNum', 'crEval', 'crEvalStudentNum', 'description', 'enrollment']
                csv_writer = csv.DictWriter(csvfile, fieldnames=fieldNames, delimiter=',')
                csv_writer.writerow({'semester': semester, 'crn': crn, 'courseLabel': courseLabel,
                                     'courseTitle': courseTitle, 'instructor': instructor,
                                     'insEval': insEvalRating, 'insEvalStudentNum': insEvalStudentCnt,
                                     'crEval': crEvalRating, 'crEvalStudentNum': crEvalStudentCnt,
                                     'description': descriptionPane, 'enrollment' : enrollment})
            yield {'semester': semester, 'crn': crn, 'courseLabel': courseLabel,
                   'courseTitle': courseTitle, 'instructor': instructor,
                   'insEval': insEvalRating, 'insEvalStudentNum': insEvalStudentCnt,
                   'crEval': crEvalRating, 'crEvalStudentNum': crEvalStudentCnt,
                   'description': descriptionPane, 'enrollment' : enrollment}

            course = BluebookscraperItem()

            course['semester'] = semester
            course['crn'] = crn
            course['course_label'] = courseLabel
            course['course_title'] = courseTitle
            course['instructor'] = instructor
            course['ins_eval'] = insEval
            course['ins_eval_student_num'] = insEvalStudentCnt
            course['cr_eval'] = crEval
            course['cr_eval_student_num'] = crEvalStudentCnt
            course['description'] = descriptionPane
            course['enrollment'] = enrollment

            yield course

    def parse(self, response):
        #open_in_browser(response)
        amount_of_courses =  len(response.css('ul#ctl00_MainContentSearchQuery_searchCriteriaEntry_CourseSubjectCombo_OptionList').css('li::text').getall())
        testCsv = "test2.csv"
        print(amount_of_courses)
        # opening the file with w+ mode truncates the file
        f = open(testCsv, "w+")
        f.close()
        with open('test2.csv', 'a', newline='') as csvfile:
            fieldNames = ['crn', 'semester', 'courseLabel', 'instructor', 'courseTitle', 'insEval', 'insEvalStudentNum',
                          'crEval', 'crEvalStudentNum', 'description', 'enrollment']
            csv_writer = csv.DictWriter(csvfile, fieldnames=fieldNames, delimiter=',')
            csv_writer.writeheader()
        for i in range(5): #switch 5 out with amount_of_courses
            #print(response.url)
            yield scrapy.Request(response.url, callback=self.fillOutForm,
                                 meta={'__EVENTTARGET': 'ctl00$MainContentSearchQuery$searchCriteriaEntry$SearchBtn',
                                       'course_id': i, 'current_page': 1, 'total_pages': 1})






































        #     new_response = self.fillOutForm(new_response, 'ctl00$MainContent$mainContent1$CourseTermSelectRBL$1', i, 1, 1)
        #     try:
        #         totalPages = int(new_response.css('input#ctl00_MainContent_mainContent1_TotalPages::attr(value)').get)
        #     except AttributeError:
        #         totalPages = 0
        #     for x in range(totalPages):
        #         new_response = self.fillOutForm(new_response, 'ctl00$MainContent$mainContent1$PagerImgBtn_NextTOP', i, x, totalPages)
        #         for index, course in enumerate(new_response.css("table.infoTable")):
        #             semester = course.css(f"span#ctl00_MainContent_mainContent1_MainContentAccordion_Pane_{index}_header_SemYrLbl::text").get()
        #             crn = course.css(f"span#ctl00_MainContent_mainContent1_MainContentAccordion_Pane_{index}_header_crnlbl::text").get()
        #             courseLabel = course.css(f"span#ctl00_MainContent_mainContent1_MainContentAccordion_Pane_{index}_header_CourseLbl ..")
        #             courseLabel = courseLabel.css("::text").get()
        #             courseTitle = course.css(f"a#ctl00_MainContent_mainContent1_MainContentAccordion_Pane_{index}_header_TitleLnkBtn::text").get()
        #             instructor = course.css(f"a#ctl00_MainContent_mainContent1_MainContentAccordion_Pane_{index}_header_InstructorLnkBtn::text").get()
        #             insEval = course.css(f"span#ctl00_MainContent_mainContent1_MainContentAccordion_Pane_{index}_header_InstEval ..")
        #             crEval = course.css(f"span#ctl00_MainContent_mainContent1_MainContentAccordion_Pane_{index}_header_CourseEval ..")
        #             insEvalData = (insEval.css('::text').get()).split('\n')
        #             try:
        #                 if "n/a" in insEvalData:
        #                     insEvalRating = 'n/a'
        #                     insEvalStudentCnt = 'n/a'
        #                 else:
        #                     insEvalRating = str(
        #                         round(float(insEvalData[1].split(" ")[0]) / float(insEvalData[1].split(" ")[2]), 2))
        #                     insEvalStudentCnt = (insEvalData[2].split(" ")[0])
        #             except ValueError:
        #                 insEvalRating = 'n/a'
        #                 insEvalStudentCnt = 'n/a'
        #             crEvalData = (crEval.css("::text").get()).split('\n')
        #             try:
        #                 if "n/a" in crEvalData:
        #                     crEvalRating = 'n/a'
        #                     crEvalStudentCnt = 'n/a'
        #                 else:
        #                     crEvalRating = str(
        #                         round((float(crEvalData[1].split(" ")[0]) / float(crEvalData[1].split(" ")[2])), 2))
        #                     crEvalStudentCnt = (crEvalData[2].split(" ")[0])
        #             except ValueError:
        #                 crEvalRating = 'n/a'
        #                 crEvalStudentCnt = 'n/a'
        #             yield{'semester': semester.text, 'crn': crn.text, 'courseLabel': courseLabel.text,
        #                                  'courseTitle': courseTitle.text, 'instructor': instructor.text,
        #                                  'insEval': insEvalRating, 'insEvalStudentNum': insEvalStudentCnt,
        #                                  'crEval': crEvalRating, 'crEvalStudentNum': crEvalStudentCnt}







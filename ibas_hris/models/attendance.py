
from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import pytz
from xlrd import open_workbook
import base64
import io
import math


DEFAULT_STANDARD_WORK_HOURS = 8.00


class ibas_attendance(models.Model):
    _inherit = 'hr.attendance'

    is_workday = fields.Boolean(compute='_compute_is_workday', string='Is Work Day?', store=True)
    grace_period = fields.Integer(string='Grace Period in Minutes', default=10, store=True)
    is_tardy = fields.Boolean(string='Is Tardy', compute="_onchange_employee_id", store=True)
    late_in_float = fields.Float(string='Lates', compute="_onchange_employee_id", store=True)
    workday = fields.Datetime(string='Date Today',compute="_onchange_employee_id", readonly=True,store=True)
    workdate = fields.Date(string='Work Date',compute="_onchange_employee_id", store=True)

    is_special = fields.Boolean(string='Is Special Holiday', compute="_onchange_employee_id", store=True)
    is_regular = fields.Boolean(string='Is Regular Holiday', compute="_onchange_employee_id", store=True)
    
    is_undertime = fields.Boolean(compute='_compute_is_undertime', string='Is Undertime', store=True)
    undertime_minutes = fields.Float(compute='_compute_is_undertime', string='Undertime Minutes', store=True)


    
    is_restday_work = fields.Boolean(string='Is Rest Day Work Day?', store=True)


    #Rest Days Work
    rest_day_hrs_wrk = fields.Float( string='Restday Work', store=True)
    rest_day_hrs_ot = fields.Float(string='Restday Overtime in Minutes', store=True)


    #Regular Workdays
    reg_wrk_ut_min = fields.Float(compute='_compute_is_undertime', string='Undertime Minutes', store=True)
    reg_late_in_float = fields.Float(string='Lates', compute="_onchange_employee_id", store=True)
    reg_appr_overtime = fields.Float( string='Overtime in Minutes', store=True)


    #Regular Holidays(Approve Work) 
    reg_hol_hrs_wrk = fields.Float( string='Holidays Work', store=True)
    reg_hol_hrs_ot = fields.Float( string='Holidays Overtime in Minutes', store=True)

    #Special Holidays(Approve Work)
    spec_hol_hrs_wrk = fields.Float( string='Holidays Work', store=True)
    spec_hol_hrs_ot = fields.Float( string='Holidays Overtime in Minutes', store=True)


    #Restday Regular Holidays(Approve Work) 
    rd_reg_hol_hrs_wrk = fields.Float( string='Restday Holidays Work', store=True)
    rd_reg_hol_hrs_ot = fields.Float( string='Restday Holidays Overtime in Minutes', store=True)

    #Restday Special Holidays(Approve Work)
    rd_spec_hol_hrs_wrk = fields.Float( string='Holidays Work', store=True)
    rd_spec_hol_hrs_ot = fields.Float( string='Holidays Overtime in Minutes', store=True)


    @api.multi
    def action_computeAttendance(self):
        for rec in self:
            rec._compute_segregate_hourswork()



    #@api.depends('check_out','is_restday_work')
    @api.onchange('employee_id','check_in','check_out','is_restday_work', 'is_special', 'is_regular')
    def _compute_segregate_hourswork(self):
        #for rec in self:
        self.rest_day_hrs_wrk = 0.00
        self.reg_appr_overtime = 0.00
        self.reg_hol_hrs_wrk = 0.00
        self.spec_hol_hrs_wrk = 0.00    
        self.rd_spec_hol_hrs_wrk = 0.00
        self.rd_reg_hol_hrs_wrk = 0.00


        #OT
        self.reg_hol_hrs_ot = 0.00
        self.spec_hol_hrs_ot = 0.00
        self.rest_day_hrs_ot = 0.00
        self.reg_appr_overtime = 0.00
        self.rd_spec_hol_hrs_ot = 0.00
        self.rd_reg_hol_hrs_ot = 0.00

        hours_work = self.worked_hours
        overtime_in_minutes = 0.0

        if self.worked_hours > DEFAULT_STANDARD_WORK_HOURS:
            hours_work = DEFAULT_STANDARD_WORK_HOURS
            self.worked_hours = DEFAULT_STANDARD_WORK_HOURS



        overtimes = self.env['ibas_hris.ot'].search(
            [('state', '=', 'approved'), ('overtime_from', '>=', self.check_in),
             ('overtime_from', '<=', self.check_out), ('employee_id', '=', self.employee_id.id)])

        if overtimes:
            for ot in overtimes:
                overtime_in_minutes += ot and ot.ot_minutes or 0.0

            if overtime_in_minutes  > 0.0:
                overtime =  (int(int(overtime_in_minutes)/30)) * 30
                overtime_in_minutes = overtime

        if self.is_undertime:
            if self.worked_hours >= 9:
                self.is_undertime = False
                self.undertime_minutes  = 0.00

                


        if self.is_restday_work:
            if self.is_special:
                self.rd_spec_hol_hrs_wrk = hours_work
                self.rd_spec_hol_hrs_ot = overtime_in_minutes                

            elif self.is_regular:
                self.rd_reg_hol_hrs_wrk = hours_work
                self.rd_reg_hol_hrs_ot = overtime_in_minutes

            else:
                self.rest_day_hrs_wrk = hours_work
                self.rest_day_hrs_ot = overtime_in_minutes
        else:
            if self.is_special:
                self.spec_hol_hrs_wrk = hours_work
                self.spec_hol_hrs_ot = overtime_in_minutes
            elif self.is_regular:
                self.reg_hol_hrs_wrk = hours_work
                self.reg_hol_hrs_ot = overtime_in_minutes
            else:
                self.reg_appr_overtime = overtime_in_minutes

    
    @api.depends('check_out')
    def _compute_is_undertime(self):
        for rec in self:
            rec.undertime_minutes = 0
            rec.is_undertime = False
            if (rec.employee_id is not False and rec.check_out != False):
                tz = pytz.timezone('Asia/Manila')
                rec.workdate =  fields.Datetime.from_string(rec.check_in).replace(tzinfo = pytz.UTC).astimezone(tz).date() #fields.Datetime.from_string(rec.check_in).date()
                if (rec.employee_id.work_sched is not False):
                    if rec.is_workday:
                        dow = fields.Date.from_string(rec.check_in).weekday()
                        cnts = rec.employee_id.work_sched.attendance_ids.search([("dayofweek","=",dow),
                        ("calendar_id","=",rec.employee_id.work_sched.id)])
                        if (cnts):
                            mylen = len(cnts)
                            myWD = cnts[mylen - 1]
                            splitTime = str(myWD.hour_to).split(".")
                            myHour = int(splitTime[0]) - 8
                            if (len(str(splitTime[1])) <= 1):
                                splitTime[1] = splitTime[1] + "0"
                            myMinute = int((float(splitTime[1]) / 100) * 60 )

                            tz = pytz.timezone('Asia/Manila')
                            check_out = fields.Datetime.from_string(rec.check_out)
                            year = check_out.year
                            month = check_out.month
                            day = check_out.day
                            
                            checker_date = fields.Datetime.from_string(rec.check_out).replace(tzinfo = pytz.UTC)
                            if check_out.day != checker_date.astimezone(tz).day:
                                day = day + 1
                    
                            myworkday = datetime(year,month,day,myHour,myMinute,0,0,pytz.UTC)
                            lapse =  myworkday - checker_date
                            if (lapse.total_seconds() > 0 ):
                                rec.undertime_minutes = (lapse.total_seconds() / 60)
                                rec.is_undertime = True

                #Check UnderTime
                if rec.is_undertime:
                    if rec.worked_hours >= 9:
                        rec.is_undertime = False
                        rec.undertime_minutes  = 0.00


                            
        
    

    is_special = fields.Boolean(string='Is Special Holiday')
    is_regular = fields.Boolean(string='Is Regular Holiday')



    # Change this to computed
    @api.depends('employee_id','check_in')
    def _onchange_employee_id(self):
         for rec in self:
            rec.late_in_float = 0
            rec.is_tardy = False
            rec.is_special = False
            rec.is_regular = False

            rec.is_undertime = False
            rec.undertime_in_float = 0



            if (rec.employee_id is not False):
                tz = pytz.timezone('Asia/Manila')
                rec.workdate = fields.Datetime.from_string(rec.check_in).replace(tzinfo = pytz.UTC).astimezone(tz).date() #fields.Datetime.from_string(rec.check_in).date()
                #SDS No CHANGES

                #date_previous = fields.Date.from_string(rec.workdate)-timedelta(days=1)                
                #with_holiday_pay = False

                #Check if Previous Day has Attendance and if Not Check if Day of that Date is a Rest Day date

                #attendance = self.env['hr.attendance'].search([('workdate', '=', date_previous),('employee_id', '=', rec.employee_id.id)])
                #if attendance:
                #    with_holiday_pay = True
                #else:
                    #Now Check if No Attendance and if Date is a Rest Day
                #    dow = date_previous.weekday()
                #    cnt = rec.employee_id.resource_calendar_id.attendance_ids.search_count([("dayofweek","=",dow)])
                #    if cnt == 0:
                #        with_holiday_pay = True

                if (rec.employee_id.work_sched is not False):
                    dow = fields.Date.from_string(rec.check_in).weekday()
                    cnts = rec.employee_id.work_sched.attendance_ids.search([("dayofweek","=",dow),
                    ("calendar_id","=",rec.employee_id.work_sched.id)])
                    if (cnts):
                        splitTime = str(cnts[0].hour_from).split(".")
                        myHour = int(splitTime[0]) - 8
                        if (len(str(splitTime[1])) <= 1):
                            splitTime[1] = splitTime[1] + "0"
                        myMinute = int((float(splitTime[1]) / 100) * 60 )

                        tz = pytz.timezone('Asia/Manila')
                        check_in = fields.Datetime.from_string(rec.check_in)
                        year = check_in.year
                        month = check_in.month
                        day = check_in.day
                        
                        checker_date = fields.Datetime.from_string(rec.check_in).replace(tzinfo = pytz.UTC)
                        if check_in.day != checker_date.astimezone(tz).day:
                            day = day + 1
                        
                        # Add check for holiday here
                        holidays = self.env['ibas_hris.holiday'].search([("date","=",checker_date.astimezone(tz).date())])
                        if len(holidays) != 0:
                            myworkday = datetime(year,month,day,myHour,myMinute,0,0,pytz.UTC)
                            rec.workday = myworkday
                            if holidays[0].holiday_type == "regular":
                                #Added By SDS To Check if the Previous Day has attendance
                                rec.is_regular = True #True
                                rec.is_workday = False
                                return
                            else:
                                rec.is_special = True #True
                                rec.is_workday = False
                                return




        
                        myworkday = datetime(year,month,day,myHour,myMinute,0,0,pytz.UTC)
                        lapse =  checker_date - myworkday
                        if (lapse.total_seconds() > 0 ):
                            rec.late_in_float = (lapse.total_seconds() / 60)
                            rec.is_tardy = True 
                        rec.workday = myworkday
                        
                    

  
    
    @api.depends('employee_id', 'check_in')
    def _compute_is_tardy(self):
        for rec in self:
            if (rec.employee_id is not False):
                if (rec.employee_id.resource_calendar_id is not False):
                    dow = fields.Date.from_string(rec.check_in).weekday()
                    cnts = rec.employee_id.resource_calendar_id.attendance_ids.search([("dayofweek","=",dow)])
                    # if (cnts):
                        # raise Warning(_(cnts[0].hour_from))
                        # splitTime = str(cnts[0].hour_from).split(".")
                        # myHour = int(splitTime[0]) - 7
                        # myMinute = int(splitTime[1])
                        # myWD = datetime.today().replace(hour=myHour,minute=myMinute,second=0)
                        # rec.workday = myWD
                        # myDate = fields.Datetime.from_string(rec.check_in)
                        
                        # workdate= fields.Datetime.from_string(rec.check_in).replace(hour=myHour)
                        # if (workdate <= myDate):
                        #     rec.late_in_float = (workdate - myDate).total_seconds()

    
   
    
    @api.depends('employee_id', 'check_in','is_special','is_regular')
    def _compute_is_workday(self):
        for rec in self:
            if (rec.employee_id is not False):
                if (rec.employee_id.resource_calendar_id is not False):
                    dow = fields.Date.from_string(rec.check_in).weekday()
                    cnt = rec.employee_id.resource_calendar_id.attendance_ids.search_count([("dayofweek","=",dow)])
                    if (cnt != 0):
                        if rec.is_special or rec.is_regular:
                            rec.is_workday = False
                        else:
                            rec.is_workday = True
                        
        
        return False


class AttendanceLoader(models.Model):
    _name = 'ibas_hris.attendance_loader'
    
    attendance_file = fields.Binary(string='CSV FILE')
    attendance_line_ids = fields.One2many('ibas_hris.attendance_loader_line', 'attendance_loader_id', string='Attendances')

    @api.multi
    def load_attendance(self):
        for rec in self:
            # For each attendance line
            for att_line in rec.attendance_line_ids:
                mydate = att_line.work_day
                ret_count = self.env['hr.attendance'].search_count([ 
                            ("workdate","=",mydate),
                            ("employee_id","=",att_line.employee_id.id)
                        ])
                if ret_count <= 0:
                    newatt = self.env['hr.attendance'].create({
                        'employee_id': att_line.employee_id.id,
                        'check_in': att_line.check_in,
                        'check_out': att_line.check_out,
                    })
                    att_line.state = 'created'
                    newatt._onchange_employee_id()
                else:
                    att_line.state = 'updated'
                
        #Check if no attendance record
        #if none, create attendance record
        #if yes, update if necessary

    @api.multi
    def loadfile(self):
        for rec in self:
            data_file = base64.b64decode(rec.attendance_file).decode('utf-8')
            lines = data_file.split('\n')
            for l in lines:
                larray = l.split("\t")
                if len(larray) > 1:    
                    biometric_id = larray[0]
                    parsed_date = larray[1]
                    dto = datetime.strptime(parsed_date, '%d/%m/%Y %H:%M') - timedelta(hours=8, minutes=0)
                    this_emp = self.env["hr.employee"].search([("bio_number","=",biometric_id)])

                    if this_emp:    
                        
                        ret_count = rec.attendance_line_ids.search_count([
                            ("attendance_loader_id","=",rec.id), 
                        ("work_day","=",dto.date()),
                        ("employee_id","=",this_emp.id)
                        ])
                        
                        if ret_count == 0:
                            self.env["ibas_hris.attendance_loader_line"].create({
                                'employee_id': this_emp.id,
                                'work_day': dto.date(),
                                'check_in': dto,
                                'attendance_loader_id': rec.id
                            })
                        else:
                            thisRec = rec.attendance_line_ids.search([
                                ("attendance_loader_id","=",rec.id), ("work_day","=",dto.date()),("employee_id","=",this_emp.id)])
                                
                                
                            if fields.Datetime.from_string(thisRec.check_in) < dto and thisRec.check_out == False:
                                thisRec.check_out = dto
                            elif fields.Datetime.from_string(thisRec.check_in) < dto and fields.Datetime.from_string(thisRec.check_out) < dto:

                                thisRec.check_out = dto
            
    
class AttendanceLoaderLine(models.Model):
    _name = 'ibas_hris.attendance_loader_line'
    
    employee_id = fields.Many2one('hr.employee', string='Employee')
    work_day = fields.Date(string='Work Day')
    check_in = fields.Datetime(string='Check In')
    check_out = fields.Datetime(string='Check Out')
    attendance_loader_id = fields.Many2one('ibas_hris.attendance_loader', string='Attendance Loader')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('created', 'Created'),
        ('updated', 'Updated')
    ], string='Status')

class IbasHoliday(models.Model):
    _name = 'ibas_hris.holiday'
    _description = 'IBAS Holidays'
    
    date = fields.Date(string='Date', required=True)
    name = fields.Char(string='Name', required=True)
    holiday_type = fields.Selection([
        ('regular', 'Regular'),
        ('special', 'Special')
    ], string='Holiday Type', required=True)   

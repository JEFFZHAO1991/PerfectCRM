from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Customer(models.Model):
    """customer table"""
    name=models.CharField(max_length=32, blank=True, null=True)
    qq = models.CharField(max_length=64, unique=True)
    qq_name = models.CharField(max_length=64, blank=True, null=True)
    phone = models.CharField(max_length=64, blank=True, null=True)
    source_choice = ((0, "referral"),
                     (1, "QQchatGroup"),
                     (2, "officialWebsite"),
                     (3, "BaiduPromotion"),
                     (4, "51CTO"),
                     (5, "ZhiHu"),
                     (6, "MarketPromotion"),
    )
    source =  models.SmallIntegerField(choices= source_choice)
    referral_form = models.CharField(verbose_name = "referralQQ", max_length=64, blank=True, null=True)
    consult_course = models.ForeignKey('Course', verbose_name="consultCourse", on_delete=models.CASCADE)
    content = models.TextField(verbose_name="ConsultDetail")
    tags = models.ManyToManyField('Tag', blank=True)
    consultant = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    note = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.qq

    class Meta:
        verbose_name = "客户表"
        verbose_name_plural = "客户表"

class Tag(models.Model):
    name = models.CharField(unique = True, max_length=32)

    def __str__(self):
        return self.name

class CustomerFollowUp(models.Model):
    customer = models.ForeignKey("Customer", on_delete = models.CASCADE)
    content = models.TextField(verbose_name="What to follow up")
    consultant = models.ForeignKey('UserProfile', on_delete = models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    intention_choice=((0,"apply within two weeks"),
                      (1,"apply within 1 month"),
                      (2,"no intention"),
                      (3,"enrolled in other institutions"),
                      (4,"enrolled"),
                      (5,"blocked"),
    )
    intention=models.SmallIntegerField(choices=intention_choice)
    def __str__(self):
        return "<%s : %s>" %(self.customer.qq_name, self.content)
class Course(models.Model):
    name = models.CharField(max_length=64, unique=True)
    price = models.SmallIntegerField()
    period = models.PositiveSmallIntegerField()
    outline = models.TextField()
    def __str__(self):
        return self.name

class Branch(models.Model):
    name = models.CharField(max_length=64, unique=True)
    addr = models.CharField(max_length=120)
    def __str__(self):
        return self.name

class ClassList(models.Model):
    branch = models.ForeignKey('Branch', on_delete=models.CASCADE)
    course =models.ForeignKey('Course', on_delete=models.CASCADE)
    class_type_choice=((0,"FaceToFace"),
                       (1,"FaceToFace(weekend)"),
                       (2,"Online")
    )
    semester =models.PositiveSmallIntegerField(verbose_name="Semester")
    teacher = models.ManyToManyField('UserProfile')
    start_date = models.DateField(verbose_name="Start date")
    end_date = models.DateField(verbose_name="End date", blank=True, null=True)
    def __str__(self):
        return "%s %s %s" %(self.branch, self.course, self.semester)
    class Meta:
        unique_together = ('branch', 'course', 'semester')


class Enrollment(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    enrolled_class = models.ForeignKey('ClassList', on_delete=models.CASCADE, verbose_name="enrolled class")
    consultant = models.ForeignKey('UserProfile', on_delete=models.CASCADE, verbose_name="consultant")
    contract_agreed = models.BooleanField(default=False, verbose_name="the student agreed")
    contract_approved = models.BooleanField(default=False, verbose_name="contract reviewed")
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return "%s %s" %(self.customer, self.enrolled_class)
    class Meta:
        unique_together = ('customer', 'enrolled_class')

class Payment(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE, verbose_name="course")
    amount = models.PositiveIntegerField(verbose_name="Amount", default=500)
    consultant = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s %s" %(self.customer, self.amount)


class StudyRecord(models.Model):
    student = models.ForeignKey("Enrollment", on_delete=models.CASCADE)
    course_record = models.ForeignKey('CourseRecord', on_delete=models.CASCADE)
    attendance_choice=((0,"signed"),
                       (1,"late"),
                       (2,"absent"),
                       (3,"drop off"))
    attendance= models.SmallIntegerField(choices=attendance_choice, default=0)

    score_choices = ((100,"A+"),
                     (90,"A"),
                     (85,"B+"),
                     (80,"B"),
                     (75,"B-"),
                     (70,"C+"),
                     (60,"C"),
                     (40,"C-"),
                     (-50,"D"),
                     (-100,"COPY"),
                     (0,"N/A")
                     )
    score = models.SmallIntegerField(choices=score_choices, default=0)
    memo = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    def __str__(self):
        return "%s %s %s" %(self.student, self.course_record, self.score)

    class Meta:
        unique_together = ('student', 'course_record')
        verbose_name_plural = "学习记录"




class CourseRecord(models.Model):
    from_class = models.ForeignKey('ClassList', verbose_name="Class", on_delete=models.CASCADE)
    day_num = models.PositiveSmallIntegerField(verbose_name="Which day")
    teacher = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    got_homework = models.BooleanField(default=True)
    homework_title = models.CharField( max_length=128, blank=True, null=True)
    homework_content = models.TextField(blank=True, null=True)
    outline = models.TextField(verbose_name="This course's outline")
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return "%s %s" %(self.from_class, self.day_num)
    class Meta:
        unique_together = ('from_class', 'day_num')


class Student(models.Model):
    """student table"""
    pass

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=32)
    roles = models.ManyToManyField('Role', blank=True)

    def __str__(self):
        return self.name

class Role(models.Model):
    name = models.CharField(max_length=32, unique=True)
    menus =models.ManyToManyField('Menu', blank=True)
    def __str__(self):
        return self.name

class Menu(models.Model):
    name = models.CharField(max_length=32)
    url_name = models.CharField(max_length=32)

    def __str__(self):
        return self.name

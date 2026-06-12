--1.addition function
--create or replace function fn_add(a number , b number)
--return number
---is
--begin
    --return a+b;
    --end;
--/
--select fn_add(18,20)
--from dual;

--2.subtraction function
--create or replace function fn_subtract(a number,b number)
--return number
--is
--begin
    --return a-b;
    --end;
--/
--select fn_subtract(20,18)
--from dual;

--3.Multiplication function
--create or replace function fn_multiplication(a number,b number)
--return number
--is
--begin
    --return a*b;
    --end;
    --/
--select fn_multiplication (16,22)
--from dual;

--4.Division function
--create or replace function fn_divide(a number,b number)
--return number
--is
--begin
    --return a/b;
    --end;
--/
--select fn_divide(250,10)
--from dual;

--5.Square function
--create or replace function fn_square(a number)
--return number
--is
--begin
    --return a*a;
    --end;
--/
--select fn_square(18)
--from dual;

--6.cube function
--create or replace function fn_cube(a number)
--return number
--is
--begin
    --return a*a*a;
    --end;
    --/
    --select fn_cube(8)
    --from dual;

--7.even or odd function
--create or replace function fn_even_odd(a number)
--return varchar2
--is
--begin
    --if mod(a,2)=0 then
    --return 'even';
    --else
    --return 'odd';
    --end if;
    --end;
--/
 --select fn_even_odd(6)
 --from dual;

--8. maximum number function
--create or replace function fn_max(a number,b number)
--return number
--is
--begin
    --if a>b then
    --return a ;
    --else
    --return b;
    --end if;
    --end;
    --/
    --select fn_max(8,9)
    --from dual;

8. maximum number function
--create or replace function fn_max(a number,b number)
--return number
--is
--begin
    --if a>b then
    --return a ;
    --else
    --return b;
    --end if;
    --end;
    --/
    --select fn_max(8,9)
    --from dual;

--9.minimum number function
--create or replace function fn_min(a number,b number)
--return number
--is
--begin
    --if a<b then
    --return a;
    --else
    --return b;
    --end if;
    --end;
    --/
    --select fn_min(10,9)
    --from dual;

--10.factorial function
--create or replace  function fn_factorial(n number)
--return number
--is
--fact number:=1;
--begin
    --for i in 1..n loop
    --fact:=fact*i;
    --end loop;
    --return  fact;
    --end;
--/
--select fn_factorial(7)
--from dual;

--11.String length function
--create or replace function fn_string_length(text varchar2)
--return number
--is
--begin
    --return length(text);
    --end;
    --/
--select fn_string_length('Girija')
--from dual;

--12.uppercase function
--create or replace function fn_uppercase(text varchar2)
--return varchar2
--is
--begin
    --return upper(text);
    --end;
    --/
--select fn_uppercase('girija yadav')
--from dual;

--13. lowercase function
--create or replace function fn_lowercase(text varchar2)
--return varchar2
--is
--begin
    --return lower(text);
    --end;
    --/
    --select fn_lowercase('GIRIJA YADAV')
    --from dual;

--14.reverse string function
--create or replace function fn_reverse(text varchar2)
--return varchar2
--is 
--begin
    --return reverse(text);
    --end;
--/
--select fn_reverse('hello')
--from dual;

15.current date function
create or replace function fn_current_date
return date
is
begin
    return sysdate; 
    end;
/
select fn_current_date
from dual;

--16.Age calculation function
--create or replace function fn_age(dob date)
--return number
--is 
--begin
    --return trunc(months_between(sysdate,dob)/12);
   -- end;
    --/
--select fn_age (to_date('2002-09-18','yyyy-mm-dd'))
--from dual;

--17.simple interest function
--create or replace function fn_simple_interest(p number,t number,r number)
--return number
--is
--begin
    --return(p*t*r)/100;
    --end;
    --/
    --select fn_simple_interest(10,0.5,6)
    --from dual;

--18.area of circle function
--create or replace function fn_circle_area(radius number)
--return number
--is
--begin
    --return 3.14*radius*radius;
    --end;
    --/
--select fn_circle_area(8)
--from dual;

--19.palindrome function
--create or replace function fn_palindrome(text varchar2)
--return varchar2
--is
--reverse_text varchar2(100):='';
--begin
    --for i in reverse 1..length(text)
    --loop
        --reverse_text:=reverse_text ||substr(text,i,1);
        --end loop;
        --if upper(text)=upper(reverse_text)then
        --return 'palindrome';
        --else
        --return 'not palindrome';
        --end if;
        --end;
       -- /
    --select fn_palindrome('madam')
    --from dual;

--20.salary hike function
--create or replace function fn_salary_hike(salary number,percent number)
--return number
--is
--begin
    --return salary +(salary*percent/100);
    --end;
    --/
    --select fn_salary_hike(20000,7)
    --from dual;
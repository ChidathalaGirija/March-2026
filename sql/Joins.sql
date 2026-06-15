1) select e.emp_name,e.emp_id,d.dept_name,d.dept_id
from employees e
innerjoin  department d
on e.dept_id= d.dept_id ;

2) select e.emp_name ,e.emp_id , d.dept_name , d.dept_id
from employees  e
Left join department d
on e.dept_id = d.dept_id ;

3)   select e.emp_name ,e.emp_id , d.dept_name , d.dept_id
from employees  e
Left join department d
on e.dept_id = d.dept_id ;

4)   select e.emp_name ,e.emp_id , d.dept_name , d.dept_id
from employees  e
full join department d
on e.dept_id = d.dept_id ;

5)  select e.emp_name ,e.emp_id , d.dept_name , d.dept_id
from employees  e
Left join department d
on e.dept_id = d.dept_id 
where d.dept_id is null;

6) select e.emp_name ,e.emp_id , d.dept_name , d.dept_id
from employees  e
Left join department d
on e.dept_id = d.dept_id 
where d.dept_id is null;

7)  select e.emp_id , d.dept_name , d.dept_id , count(emp_id)
from employees e
left join department d
on e.dept_id = d.dept_id 
group by dept_name;

8) select e.emp_id , d.dept_name, avg(salary)
from employees e
left join departments d
on e.dept_id = d.dept_id
group by dept_name;

9) select e.emp_id,d.dept_id, e.salary
from 
(
select e.emp_id , e.salary , d.dept_id,
dense_rank()over(partition by  dept_id order by salary desc) as rnk
from employees e
left join department d
on e.dept_id = d.dept_id
) t
where rnk>1;

10) select  e. emp_name ,d.dept_name  
from employees e
left join departments d
on e.dept_id = d.dept_id   
where e.hire_date>='2024-01-01;

11) select e.emp_name,
coalesce (d.dept_name,'no department') as dept_name
from employees e
left join departments d
on e.dept_id = d.dept_id;

12)  select d.dept_name , count(e.emp_id) 
from departments d
join emloyees e
on d.dept_id =e.dept_id
group by d.dept_name
having count(e.emp_id)>1;

13)  select d.location , sum(e.salary)
from departments d
left join employees e
on d.dept_id = e.dept_id
group by d.location;

14) select e.emp_name,d.dept_name,d.location
from employees e
join departments d
on e.dept_id = d.dept_id
where d.location ='benguluru';

15) select * 
from 
(
select  d.dept_id,e.emp_name, e.salary,
row_number()over(partition by dept_id order by salary desc)rn
from employees e
)t
where rn =1;

16)  select e.emp_name , e.emp_id ,d.dept_id ,d.dept_name ,e.salary
from departments d
join employees e 
on d.dept_id = e.dept_id
group  by d.dept_name
having count(e.salary)=0;

17)  select e.emp_name , d.dept_name ,d.dept_id 
from departments d
where not exists(
select 1
from employees e
where e.dept_id = d.dept_id
);

18)  select count(*) as total
from employees
where dept_id is null;

19)  select e.emp_name , d.dept_name
from employees e
cross join departments d;

20) select e.emp_id , d.dept_name , d.dept_id, e.emp_name
from employees  e
Left join department d
on e.dept_id = d.dept_id ;

select e.emp_id , d.dept_name , d.dept_id, e.emp_name
from employees  e
inner join department d
on e.dept_id = d.dept_id ;





































































































































































































































































































































































































































































































































































































































8)  








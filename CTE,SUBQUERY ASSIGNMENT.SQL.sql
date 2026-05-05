--Create Table airlines(
    --airline_id int primary key,
    --airline_name varchar(100),
    --country varchar(50)
--);
--insert into airlines values(1,'air india','india'),
                           -- (2,'indigo','india'),
                           -- (3,'emirates','uae'),
                            --(4,'qatar airways','qatar');
--create Table flights (
   -- flight_id number primary key,
   -- airline_id number,
    --source varchar2(50),
    --destination varchar2(50),
    --departure_time date,
    --arrival_time DATE,
     --price decimal(10,2),
    --foreign key (airline_id)
   --REFERENCES airlines(airline_id)); 
--insert into flights values(101,1,'delhi','mumbai',to_date('2026-04-01 08:00:00','yyyy-mm-dd hh24:mi:ss'),to_date('2026-04-01 10:00:00','yyyy-mm-dd hh24:mi:ss'),600),
--(102,1,'mumbai','banglore',to_date('2026-04-02 09:00:00','yyyy-mm-dd hh24:mi:ss'),to_date('2026-04-02 11:30:00','yyyy-mm-dd hh24:mi:ss'),750),
--(103,2,'delhi','banglore',to_date('2026-04-01 07:00:00','yyyy-mm-dd hh24:mi:ss'),to_date('2026-04-01 10:00:00','yyyy-mm-dd hh24:mi:ss'),500),
--(104,2,'banglore','chennai',to_date('2026-04-03 06:00:00','yyyy-mm-dd hh24:mi:ss'),to_date('2026-04-03 07:00:00','yyyy-mm-dd hh24:mi:ss'),300),
--(105,3,'dubai','delhi',to_date('2026-04-01 02:00:00','yyyy-mm-dd hh24:mi:ss'),to_date('2026-04-01 07:00:00','yyyy-mm-dd hh24:mi:ss'),1200),
--(106,3,'delhi','dubai',to_date('2026-04-02 03:00:00','yyyy-mm-dd hh24:mi:ss'),to_date('2026-04-02 08:00:00','yyyy-mm-dd hh24:mi:ss'),1100),
--(107,4,'doha','mumbai',to_date('2026-04-01 04:00:00','yyyy-mm-dd hh24:mi:ss'),to_date('2026-04-01 09:00:00','yyyy-mm-dd hh24:mi:ss'),1300),
--(108,4,'mumbai','doha',to_date('2026-04-02 05:00:00','yyyy-mm-dd hh24:mi:ss'),to_date('2026-04-02 10:00:00','yyyy-mm-dd hh24:mi:ss'),1250),
--(109,1,'delhi','mumbai',to_date('2026-04-01 08:00:00','yyyy-mm-dd hh24:mi:ss'),to_date('2026-04-01 10:00:00','yyyy-mm-dd hh24:mi:ss'),600),
--(110,2,'delhi','banglore',to_date('2026-04-04 07:00:00','yyyy-mm-dd hh24:mi:ss'),to_date('2026-04-04 10:00:00','yyyy-mm-dd hh24:mi:ss'),550);

--with all_flights as(
    --select FLIGHT_ID,price
    --from FLIGHTS
    --where price>500
--)
--select *
--from all_flights;

--with airlines_a as(
    --select airline_name
    --from AIRLINES
--)
--select source,destination,Price
--from FLIGHTS f
--join airlines a
--on f.AIRLINE_ID = a.AIRLINE_ID;


--with avg_price as(
   -- select avg(price)as avg_price
    --from FLIGHTS
--)
--select flight_id,price
--from flights,avg_price
--where price > avg_price;


--with airlines_avg as(
 --   select  a.airline_name,avg(f.price)as avg_price
   -- from airlines a
  --  join flights f
  --  on a.AIRLINE_ID = f.AIRLINE_ID
   -- group by a.airline_name
--)
--select airline_name,avg_price
--from airlines_avg
--where avg_price > 700;

   -- with ranked_flights as(
       -- select airline_name,
       -- price,
        --Rank()over(partition by airline_name order by price desc)as price_rank
         --from flights f
           -- join airlines a
            --on f.airline_id = a.airline_id
    --)
        --select airline_name,price,
       -- price_rank
               -- from ranked_flights
               -- order by airline_name desc,price_rank;

--with ranked_flights as(
    --select airline_name,flight_id,price,
    --row_number()over(partition by airline_name order by price desc)as rn
    --from flights f
    --join airlines a
    --on f.AIRLINE_ID = a.AIRLINE_ID
    
--)
--select airline_name,flight_id,price
--from ranked_flights
--where rn=1;

--with all_flights(flight_id,airline_id,destination,country,source)as(
   -- select airline_id,flight_id,destination,country
   -- from FLIGHTS
    --where source ='country'
    --union ALL
    --select airline_id,flight_id,destination,country,source
   -- from flights f
    --join airlines a
    --on f.airline_id = a.airline_id
--)
--select * 
--from all_flights;

--with all_flights as(
    --select airline_id,source,destination,departure_time,flight_id, 
   -- row_number()over(PARTITION by source,destination,departure_time order by flight_id desc)as rnk
    --from FLIGHTS f 
--)
--select *
--from all_flights 
--where rnk>1;

--with cte as(
    --select flight_id,price,departure_time,airline_name,
    --sum(price)over(partition by airline_name order by departure_time)as running_totals
    --from flights f
    --join airlines a
    --on f.airline_id = a.airline_id
--)
--select *
--from cte;


--with total_flights as(
  --  select airline_name,count(flight_id) as total_flights
   -- from FLIGHTS F
   -- join airlines a
    --on f.AIRLINE_ID =a.AIRLINE_ID
   -- group by airline_name
    
--),
--avg_price as(
    --select airline_name,avg(price) as avg_price
    --from flights f
    --join airlines a
    --on f.AIRLINE_ID = a.AIRLINE_ID
   -- group by airline_name
--)
--select t.airline_name,t.total_flights,ap.avg_price
--from total_flights t
--join avg_price ap
--on t.airline_name = ap.airline_name;

--select flight_id,Price
--from FLIGHTS
--where price>500;

--select a.airline_name,f.source,f.destination,f.price,f.flight_id
--from flights f
--join airlines a
--on f.AIRLINE_ID = a.AIRLINE_ID;

--select airline_name,avg_price
--FROM  

--(
    --select a.airline_name,avg(f.price) as avg_price
    --from flights f
    --join airlines a
    --on f.airline_id = a.airline_id
    --group by a.airline_name
--);

--select airline_name,avg_price
--FROM
--(
    --select a.airline_name,avg(f.price)as avg_price
   -- from flights f
    --join airlines a
    --on f.AIRLINE_ID = a.AIRLINE_ID
    --group by a.AIRLINE_NAME

--)
--where avg_price > 700;

--select flight_id,airline_name,Price,rank_no
--from
--(
    --select f.flight_id,a.airline_name,f.price,
    --Rank()over(partition by a.airline_name order by f.price desc)as rank_no
    --from flights f
    --join airlines a
    --on f.AIRLINE_ID = a.AIRLINE_ID
--)
    --order by airline_name,rank_no desc;

--select airline_name,FLIGHT_ID,price
--FROM
--(
--select a.AIRLINE_NAME,f.FLIGHT_ID,f.price,
--row_number()over(partition by a.airline_name order by f.price desc)as rnk
--from flights f
--join airlines a
--on f.AIRLINE_ID = a.AIRLINE_ID
--)
--where rnk=1;

--select flight_id,source,destination,departure_time
--FROM
--(
  -- select flight_id,source,destination,departure_time,
   --row_number()over(partition by source,destination,departure_time order by flight_id)as rnk
   --from flights
--)
--where rnk>1;

--select airline_name,Price,running_total
--FROM
--(
    --select a.airline_name,f.price,
    --sum(price)over(partition by a.airline_name order by f.price)as running_total
    --from flights f
    --join airlines a
    --on f.AIRLINE_ID = a.AIRLINE_ID
--);

--select airline_name,total_flights,avg_price
--FROM
--(
   -- select a.airline_name,count(flight_id)as total_flights,
    --avg(price)as avg_price
    --from flights f
    --join airlines a
    --on f.AIRLINE_ID = a.AIRLINE_ID
    --group by a.AIRLINE_NAME
--);
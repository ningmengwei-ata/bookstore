最终达成source .sql即可达成 【暂未实现


ALTER TABLE search_author ADD COLUMN tsv_column tsvector;           
UPDATE search_author SET tsv_column = to_tsvector('zh', coalesce(author,''));   
CREATE INDEX idx_gin_author ON search_author USING GIN(tsv_column);  
CREATE TRIGGER trigger_name BEFORE INSERT OR UPDATE  ON search_author FOR EACH ROW EXECUTE PROCEDURE
tsvector_update_trigger(tsv_column, 'zh', author);
SELECT * FROM search_author WHERE tsv_column @@ '杨红樱';
SELECT DISTINCT * FROM search_author WHERE tsv_column @@ '红'
SELECT * FROM search_author WHERE tsv_column @@ '美'//好家伙，杨找不到了:D
SELECT DISTINCT book_id,title,author,book_intro from book where book.book_id in 
(SELECT store.book_id from store where store_id ='1' and store.book_id in(SELECT DISTINCT book_id FROM search_author WHERE tsv_column @@ '杨'));
SELECT DISTINCT book_id,title,author,book_intro from book where book.book_id in (SELECT DISTINCT book_id FROM search_author WHERE tsv_column @@ '杨');
ALTER TEXT SEARCH CONFIGURATION zhl ADD MAPPING FOR n,v,a,i,e,l,j WITH simple;

CREATE TEXT SEARCH CONFIGURATION zh (PARSER = zhparser);
GRANT ALL PRIVILEGES ON all tables in schema public TO postgres;


DROP TABLE search_book_intro;
ALTER TABLE search_book_intro ADD COLUMN tsv_column tsvector; 
UPDATE search_book_intro SET tsv_column = to_tsvector('zh',coalesce(book_intro,''));// 20000条数据的时候这个update的速度也是可以接受的


CREATE INDEX idx_gin_zh ON search_book_intro USING GIN(tsv_column); //建立Bit Index Map索引
CREATE TRIGGER sear BEFORE INSERT OR UPDATE  ON search_book_intro FOR EACH ROW EXECUTE PROCEDURE
tsvector_update_trigger(tsv_column, 'zh', book_intro);//创建触发器
SELECT * FROM search_book_intro WHERE tsv_column @@ '美丽';
EXPLAIN ANALYZE SELECT * FROM search_book_intro WHERE tsv_column @@ '美丽';//在163155条数据中搜索结果
-- Bitmap Heap Scan on search_book_intro  (cost=12.76..339.07 rows=98 width=34) (actual time=0.040..0.130 rows=104 loops=1)
--   Recheck Cond: (tsv_column @@ '''美丽'''::tsquery)
--   Heap Blocks: exact=100
--   ->  Bitmap Index Scan on idx_gin_zh  (cost=0.00..12.73 rows=98 width=0) (actual time=0.027..0.028 rows=104 loops=1)
--         Index Cond: (tsv_column @@ '''美丽'''::tsquery)
-- Planning Time: 0.157 ms
-- Execution Time: 0.155 ms
EXPLAIN ANALYZE SELECT * FROM search_book_intro WHERE search_id > 1000;
-- Seq Scan on search_book_intro  (cost=0.00..4333.44 rows=162146 width=34) (actual time=0.870..22.562 rows=162155 loops=1)
--   Filter: (search_id > 1000)
--   Rows Removed by Filter: 1000
-- Planning Time: 0.088 ms
-- Execution Time: 32.450 ms
EXPLAIN ANALYZE SELECT DISTINCT book_id FROM search_book_intro WHERE book_id in (SELECT book_id FROM search_book_intro WHERE tsv_column @@ '美丽') LIMIT 100
-- Limit  (cost=4719.78..4720.78 rows=100 width=4) (actual time=36.313..36.343 rows=100 loops=1)
--   ->  HashAggregate  (cost=4719.78..4737.73 rows=1795 width=4) (actual time=36.312..36.331 rows=100 loops=1)
--         Group Key: search_book_intro.book_id
--         Batches: 1  Memory Usage: 73kB
--         ->  Hash Join  (cost=341.50..4715.30 rows=1795 width=4) (actual time=1.014..35.925 rows=1976 loops=1)
--               Hash Cond: (search_book_intro.book_id = search_book_intro_1.book_id)
--               ->  Seq Scan on search_book_intro  (cost=0.00..3925.55 rows=163155 width=4) (actual time=0.649..15.253 rows=163155 loops=1)
--               ->  Hash  (cost=340.28..340.28 rows=97 width=4) (actual time=0.232..0.234 rows=104 loops=1)
--                     Buckets: 1024  Batches: 1  Memory Usage: 12kB
--                     ->  HashAggregate  (cost=339.31..340.28 rows=97 width=4) (actual time=0.200..0.215 rows=104 loops=1)
--                           Group Key: search_book_intro_1.book_id
--                           Batches: 1  Memory Usage: 24kB
--                           ->  Bitmap Heap Scan on search_book_intro search_book_intro_1  (cost=12.76..339.07 rows=98 width=4) (actual time=0.063..0.171 rows=104 loops=1)
--                                 Recheck Cond: (tsv_column @@ '''美丽'''::tsquery)
--                                 Heap Blocks: exact=100
--                                 ->  Bitmap Index Scan on idx_gin_zh  (cost=0.00..12.73 rows=98 width=0) (actual time=0.045..0.045 rows=104 loops=1)
--                                       Index Cond: (tsv_column @@ '''美丽'''::tsquery)
-- Planning Time: 0.223 ms
-- Execution Time: 36.407 ms
EXPLAIN ANALYZE SELECT DISTINCT book_id FROM search_book_intro  WHERE tsv_column @@ '美丽' LIMIT 100


EXPLAIN ANALYZE SELECT * FROM search_book_intro 

SELECT COUNT(*) FROM search_book_intro
 

SELECT * from search_book_intro limit 1;
 
 CREATE EXTENSION zhparser;
 CREATE TEXT SEARCH CONFIGURATION zhl (PARSER = zhparser);
 

 
 
 
 
 
ALTER TABLE search_book_tags ADD COLUMN tsv_column tsvector;           
UPDATE search_book_tags SET tsv_column = to_tsvector('zh', coalesce(tags,''));   
CREATE INDEX idx_gin_tag ON search_book_tags USING GIN(tsv_column);  
CREATE TRIGGER trigger_name BEFORE INSERT OR UPDATE  ON search_book_tags FOR EACH ROW EXECUTE PROCEDURE
tsvector_update_trigger(tsv_column, 'zh', tags);
select * from search_book_tags limit 1;
SELECT * FROM search_book_tags WHERE tsv_column @@ '传记';


ALTER TABLE search_title ADD COLUMN tsv_column tsvector;           
UPDATE search_title SET tsv_column = to_tsvector('zh', coalesce(title,''));   
CREATE INDEX idx_gin_title ON search_title USING GIN(tsv_column);  
CREATE TRIGGER trigger_name BEFORE INSERT OR UPDATE  ON search_title FOR EACH ROW EXECUTE PROCEDURE
tsvector_update_trigger(tsv_column, 'zh', title);
select * from search_title limit 1;
SELECT * FROM search_title WHERE tsv_column @@ '狗'; 

---探究索引效果
EXPLAIN ANALYZE SELECT book_id FROM search_book_intro WHERE tsv_column @@ '美丽';

SELECT COUNT(*)









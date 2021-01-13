-- 直接执行search-index.sql即可导入文件
-- 配置zhparser只需要执行一次，不然会报错
CREATE EXTENSION zhparser;
CREATE TEXT SEARCH CONFIGURATION zh (PARSER = zhparser);
ALTER TEXT SEARCH CONFIGURATION zh ADD MAPPING FOR n,v,a,i,e,l,j WITH simple;


-- init_book_intro
ALTER TABLE search_book_intro ADD COLUMN tsv_column tsvector; 
UPDATE search_book_intro SET tsv_column = to_tsvector('zh', coalesce(book_intro''));   
CREATE INDEX idx_gin_zh ON search_book_intro USING GIN(tsv_column); 
CREATE TRIGGER trigger_name BEFORE INSERT OR UPDATE  ON search_book_intro FOR EACH ROW EXECUTE PROCEDURE
tsvector_update_trigger(tsv_column, 'zh', book_intro);
UPDATE search_book_intro SET tsv_column = to_tsvector('zh', coalesce(book_intro,''));
-- init_book_tags
ALTER TABLE search_book_tags ADD COLUMN tsv_column tsvector;           
UPDATE search_book_tags SET tsv_column = to_tsvector('zh', coalesce(tags,''));   
CREATE INDEX idx_gin_tag ON search_book_tags USING GIN(tsv_column);  
CREATE TRIGGER trigger_name BEFORE INSERT OR UPDATE  ON search_book_tags FOR EACH ROW EXECUTE PROCEDURE
tsvector_update_trigger(tsv_column, 'zh', tags);
-- search-test-case:
select * from search_book_tags limit 1;
SELECT * FROM search_book_tags WHERE tsv_column @@ '传记';


-- search-test-case
ALTER TABLE search_author ADD COLUMN tsv_column tsvector;           
UPDATE search_author SET tsv_column = to_tsvector('zh', coalesce(author,''));   
CREATE INDEX idx_gin_author ON search_author USING GIN(tsv_column);  
CREATE TRIGGER trigger_name BEFORE INSERT OR UPDATE  ON search_author FOR EACH ROW EXECUTE PROCEDURE
tsvector_update_trigger(tsv_column, 'zh', author);
SELECT * from search_author limit 20;
SELECT * FROM search_author WHERE tsv_column @@ '杨红';

--search-test-case
ALTER TABLE search_title ADD COLUMN tsv_column tsvector;           
UPDATE search_title SET tsv_column = to_tsvector('zh', coalesce(title,''));   
CREATE INDEX idx_gin_title ON search_title USING GIN(tsv_column);  
CREATE TRIGGER trigger_name BEFORE INSERT OR UPDATE  ON search_title FOR EACH ROW EXECUTE PROCEDURE
tsvector_update_trigger(tsv_column, 'zh', title);
select * from search_title limit 1;
SELECT * FROM search_title WHERE tsv_column @@ '狗';
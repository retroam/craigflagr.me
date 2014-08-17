select_query_zip = '''
    SELECT heading, flagged_status, body, external_url
    FROM Postings
    WHERE zipcode = %s
    LIMIT 5;
                    '''

select_query_full = '''
    SELECT heading, flagged_status, body, external_url
    FROM Postings
    WHERE zipcode = '{0}'
    AND category = '{1}'
    AND category_group = '{2}'
    GROUP BY id
    LIMIT 5;
                    '''
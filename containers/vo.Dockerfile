FROM tomcat:8-jdk8-corretto as VOServer

ADD https://s3.data.csiro.au/dapprd/000017515v011/data/casda_vo_tools.war?response-content-disposition=attachment%3B%20filename%3Dcasda_vo_tools.war&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20240214T080840Z&X-Amz-SignedHeaders=host&X-Amz-Expires=172800&X-Amz-Credential=4DBNNZIU07VWBFR765OA%2F20240214%2FCDC%2Fs3%2Faws4_request&X-Amz-Signature=e343015aa1bf9f0ced47dc02691401843b9db25dbed896b0135fd7d259510f58 /usr/local/tomcat/webapps/

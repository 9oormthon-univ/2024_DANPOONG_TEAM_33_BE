package com.example.onetry.exception.handler;

import com.example.onetry.common.CommonResponseDto;
import com.example.onetry.exception.CustomException;
import com.example.onetry.exception.ExceptionCode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.MalformedJwtException;
import io.jsonwebtoken.io.DecodingException;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.MediaType;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;

@Slf4j
public class JwtExceptionHandlerFilter extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain) throws ServletException, IOException {
        try {
            filterChain.doFilter(request, response);
        } catch(ExpiredJwtException e){
            setErrorResponse(response, ExceptionCode.TOKEN_EXPIRED);
        } catch (DecodingException e) { //jwt 디코딩 중 발생할 수 있는 예외. Base64 형식이 아닌경우, 헤더,페이로드,서명이 유효하지 않은경우, 페이로드 파싱에 문제가 있는경우
            setErrorResponse(response, ExceptionCode.TOKEN_INVALID);
            log.info("[JwtExceptionHandlerFilter] error name = DecodingException");
        } catch (MalformedJwtException e) { //jwt 형식이 잘못되었을 때 발생, 헤더,페이로드,서명 누락 또는 잘못된 형식.
            setErrorResponse(response, ExceptionCode.TOKEN_INVALID);
            log.info("[JwtExceptionHandlerFilter] error name = MalformedJwtException");
        } catch (IllegalArgumentException e) { // 잘못된 인수나 인수의 값이 올바르지 않을 때 발생
            setErrorResponse(response, ExceptionCode.TOKEN_INVALID);
            log.info("[JwtExceptionHandlerFilter] error name = IllegalArgumentException");
        } catch (NullPointerException e) { //참조하는 객체가 없는 상태에서 해당 객체의 멤버나 메서드에 접근하려고 할 때.
            setErrorResponse(response, ExceptionCode.TOKEN_NOT_FOUND);
            log.info("[JwtExceptionHandlerFilter] error name = NullPointerException");
        }
    }
    private void setErrorResponse(HttpServletResponse response,
                                  ExceptionCode exceptionMessage) {
        ObjectMapper objectMapper = new ObjectMapper();
        response.setStatus(exceptionMessage.getStatus().value());
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        response.setCharacterEncoding("UTF-8");

        CommonResponseDto commonResponse = new CommonResponseDto(exceptionMessage.getMessage(),null);
        try {
            response.getWriter().write(objectMapper.writeValueAsString(commonResponse));
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}

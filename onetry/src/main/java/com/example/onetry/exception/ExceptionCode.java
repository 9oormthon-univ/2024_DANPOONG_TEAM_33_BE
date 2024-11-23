package com.example.onetry.exception;

import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
public enum ExceptionCode {
    // User Exception
    USER_NOT_EXIST(HttpStatus.BAD_REQUEST, "해당 유저가 존재하지 않습니다."),
    USER_DUPLICATED_EMAIL(HttpStatus.BAD_REQUEST, "이미 존재하는 이메일입니다."),

    // Resume Exception
    RESUME_NOT_EXIST(HttpStatus.BAD_REQUEST, "이력서가 존재하지 않습ㄴ다."),

    // File Exception
    FILE_WRITE_ERROR(HttpStatus.BAD_REQUEST, "파일을 쓰던 중 문제가 발생했습니다."),
    FILE_DELETE_ERROR(HttpStatus.BAD_REQUEST, "파일을 시스템에서 삭제하던 중 문제가 발생했습니다."),
    FILE_READ_ERROR(HttpStatus.BAD_REQUEST, "파일을 시스템에서 읽어오던 중 문제가 발생했습니다."),
    FILE_NOT_EXIST(HttpStatus.BAD_REQUEST, "파일이 존재하지 않습니다."),

    // Certification Exception
    CERTIFICATION_NOT_EXIST(HttpStatus.BAD_REQUEST,"해당 자격증이 존재하지 않습니다."),

    // Portfolio Exception
    PORTFOLIO_NOT_EXIST(HttpStatus.BAD_REQUEST, "해당 포트폴리오가 존재하지 않습니다."),

    // Transcript Exception
    TRANSCRIPT_NOT_EXIST(HttpStatus.BAD_REQUEST, "해당 성적 증명서가 존재하지 않습니다."),

    // Volunteering Exception
    VOLUNTEERING_NOT_EXIST(HttpStatus.BAD_REQUEST, "해당 봉사활동이 존재하지 않습니다."),

    // UserPreference Exception
    USER_PREFERENCE_NOT_EXIST(HttpStatus.BAD_REQUEST, "해당 유저 선호 데이터가 존재하지 않습니다."),

    // MyPage Exception
    MY_PAGE_NOT_EXIST(HttpStatus.BAD_REQUEST, "해당 마이 페이지가 존재하지 않습니다."),

    // Application & APPLY Exception
    APPLICATION_NOT_EXIST(HttpStatus.BAD_REQUEST, "해당 지원서(지원서 보관 페이지)가 존재하지 않습니다."),
    APPLY_NOT_EXIST(HttpStatus.BAD_REQUEST, "해당 지원서(지원페이지) 가 존재하지 않습니다."),

    // UnAuthorize
    UNAUTHORIZED_ACCESS_CERTIFICATION(HttpStatus.BAD_REQUEST, "해당 자격증을 조회할 권한이 없습니다."),
    UNAUTHORIZED_ACCESS_PORTFOLIO(HttpStatus.BAD_REQUEST,"해당 포트폴리오를 조회할 권한이 없습니다."),
    UNAUTHORIZED_ACCESS_APPLICATION(HttpStatus.BAD_REQUEST,"해당 지원서에 조회할 권한이 없습니다."),

    // JWT Exception
    TOKEN_EXPIRED(HttpStatus.UNAUTHORIZED,  "Token 이 만료되었습니다."),
    TOKEN_INVALID(HttpStatus.UNAUTHORIZED, "토큰이 유효하지 않습니다."),
    TOKEN_NOT_FOUND(HttpStatus.BAD_REQUEST, "토큰이 비었거나 null입니다"),
    ;

    private final HttpStatus status;
    private final String message;

    ExceptionCode(HttpStatus status, String message){
        this.status =status;
        this.message = message;
    }}

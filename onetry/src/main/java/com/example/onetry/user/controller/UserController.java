package com.example.onetry.user.controller;

import com.example.onetry.common.CommonResponseDto;
import com.example.onetry.user.dto.req.SignInReqDto;
import com.example.onetry.user.dto.req.SignUpUserReqDto;
import com.example.onetry.user.dto.req.UpdateUserInfo;
import com.example.onetry.user.dto.res.SignInResDto;
import com.example.onetry.user.dto.res.UserInfoResDto;
import com.example.onetry.user.service.UserService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.log4j.Log4j2;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import static org.apache.tomcat.util.http.fileupload.FileUploadBase.MULTIPART_FORM_DATA;

@Tag(name = "[User] 유저, 프로필 사진을 수정, 조회, 삭제, 수정합니다.")
@RestController
@Log4j2
@RequiredArgsConstructor
@RequestMapping("/users")
public class UserController {

    private final UserService userService;

    @Operation(summary = "유저 정보 조회", description = "토큰 정보 기반 유저 정보를 조회합니다")
    @GetMapping("/info")
    public ResponseEntity<CommonResponseDto<UserInfoResDto>> getUserInfo(
            @AuthenticationPrincipal UserDetails userDetails){
        String email = userDetails.getUsername();
        UserInfoResDto userInfoResDto = userService.getUserInfo(email);
        return ResponseEntity.status(HttpStatus.OK).body(new CommonResponseDto<>(
                        "유저 정보 조회를 성공적으로 완료하였습니다.",
                        userInfoResDto
        ));
    }

    @Operation(summary = "프로필 사진 조회",description = "유저의 프로필 사진을 조회합니다.")
    @GetMapping("/profile")
    public ResponseEntity<byte[]> findProfileImg(
            @AuthenticationPrincipal UserDetails userDetails) {
        return ResponseEntity.status(HttpStatus.OK).contentType(MediaType.IMAGE_PNG).body(
                userService.downloadProfileFromFileSystem(userDetails.getUsername())
        );
    }

    @Operation(summary = "프로필 사진 수정",description = "유저의 프로필 사진을 수정 합니다." +
            "<br> 유저의 Token 으로 유저를 구분짓습니다.")
    @PutMapping(consumes = MULTIPART_FORM_DATA)
    public ResponseEntity<CommonResponseDto<UserInfoResDto>> updateProfileToFileSystem(
            @AuthenticationPrincipal UserDetails userDetails,
            @RequestParam("file") MultipartFile updateFile) throws Exception {
        String email = userDetails.getUsername();
        log.info("[updateProfile] 유저의 프로필 사진을 수정합니다. userEmail : {}", email);
        UserInfoResDto updateProfileImgUser = userService.updateProfileImg(email, updateFile);
        return ResponseEntity.status(HttpStatus.OK).body(new CommonResponseDto<>(
                        "프로필 사진 수정을 성공적으로 완료하였습니다.",
                        updateProfileImgUser
        ));
    }

    @Operation(summary = "유저 로그인", description = "입력한 정보로 로그인을 수행합니다. ")
    @PostMapping("/sign-in")
    public ResponseEntity<CommonResponseDto<SignInResDto>> signIn(
            @RequestBody SignInReqDto signInReqDto){
        SignInResDto signInResDto= userService.signIn(signInReqDto);
        return ResponseEntity.status(HttpStatus.OK).body(new CommonResponseDto<>(
                        "유저 로그인을 성공적으로 완료하였습니다.",
                        signInResDto
        ));
    }

    @Operation(summary = "유저 회원가입",description = "입려한 정보로 회원가입을 수행합니다. ")
    @PostMapping("/sign-up")
    public ResponseEntity<CommonResponseDto<UserInfoResDto>> signUp(
            @RequestBody SignUpUserReqDto signUpUserReqDto){
        UserInfoResDto userInfoResDto = userService.createUser(signUpUserReqDto);
        return ResponseEntity.status(HttpStatus.OK).body(new CommonResponseDto<>(
                        "유저 회원가입을 성공적으로 완료하였습니다.",
                        userInfoResDto
        ));
    }

    @Operation(summary = "유저 정보 수정",description = "해당 유저의 정보를 수정합니다. " + "<br> 아직까진 이름만 변경")
    @PatchMapping("/update")
    public ResponseEntity<CommonResponseDto<UserInfoResDto>> updateUserInfo(
            @AuthenticationPrincipal UserDetails userDetails,
            @RequestBody UpdateUserInfo updateUserInfo){
        UserInfoResDto userInfoResDto = userService.updateUserInfo(userDetails.getUsername(), updateUserInfo);
        return ResponseEntity.status(HttpStatus.OK).body(new CommonResponseDto<>(
                        "유저 정보 수정이 성공적으로 완료되었습니다.",
                        userInfoResDto
        ));
    }

    @Operation(summary = "유저 삭제", description = "토큰 정보 기반으로 유저를 삭제합니다.")
    @DeleteMapping("/delete")
    public ResponseEntity<CommonResponseDto<Void>> deleteUser(
            @AuthenticationPrincipal UserDetails userDetails){
        userService.deleteUserInfo(userDetails.getUsername());
        return ResponseEntity.status(HttpStatus.OK).body(new CommonResponseDto<>(
                        "유저 삭제가 성공적으로 완료되었습니다.",
                        null
        ));
    }

    @Operation(summary = "엑세스 토큰 재발급", description = "RefreshToken 을 통해 AccessToken 재발급"+
            "<br> 엑세스 토큰이 만료되어 401 에러가 발생하면, RefreshToken을 헤더에 담아 요청"+
            "<br>  AccessToken과 RefreshToken 을 재발급")
    @PostMapping("/reissue")
    public ResponseEntity<CommonResponseDto<SignInResDto>> reissue(HttpServletRequest request){
        SignInResDto signInResDto = userService.reissueAccessToken(request);
        return ResponseEntity.status(HttpStatus.OK).body(
                new CommonResponseDto<>(
                        "리프레시 토큰으로 엑세스 토큰 재발급 성공",
                        signInResDto));
    }
}

 //"https://dcu-speakers.store:8888/uploads/company/images/default.jpg"
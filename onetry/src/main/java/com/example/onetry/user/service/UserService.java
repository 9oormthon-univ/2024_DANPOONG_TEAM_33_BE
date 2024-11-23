package com.example.onetry.user.service;

import com.example.onetry.component.file.FileComponent;
import com.example.onetry.exception.CustomException;
import com.example.onetry.exception.ExceptionCode;
import com.example.onetry.jwt.JwtProvider;
import com.example.onetry.jwt.redis.RefreshToken;
import com.example.onetry.jwt.redis.RefreshTokenRepository;
import com.example.onetry.mypage.entity.MyPage;
import com.example.onetry.mypage.repository.MyPageRepository;
import com.example.onetry.resume.entity.Education;
import com.example.onetry.resume.entity.Experience;
import com.example.onetry.resume.entity.Resume;
import com.example.onetry.resume.repository.EducationRepository;
import com.example.onetry.resume.repository.ExperienceRepository;
import com.example.onetry.resume.repository.ResumeRepository;
import com.example.onetry.user.dto.req.SignInReqDto;
import com.example.onetry.user.dto.req.SignUpUserReqDto;
import com.example.onetry.user.dto.req.UpdateUserInfo;
import com.example.onetry.user.dto.res.SignInResDto;
import com.example.onetry.user.dto.res.UserInfoResDto;
import com.example.onetry.user.entity.User;
import com.example.onetry.user.repository.UserRepository;
import com.example.onetry.userpreference.entity.UserPreference;
import com.example.onetry.userpreference.repository.UserPreferenceRepository;
import com.example.onetry.util.FileNameGenerator;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.log4j.Log4j2;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.util.ArrayList;
import java.util.List;

@Service
@RequiredArgsConstructor
@Log4j2
@Transactional
public class UserService {
    private final UserRepository userRepository;
    private final JwtProvider jwtProvider;
    private final PasswordEncoder passwordEncoder;
    private final FileComponent fileComponent;
    private final ResumeRepository resumeRepository;
    private final ExperienceRepository experienceRepository;
    private final EducationRepository educationRepository;
    private final MyPageRepository myPageRepository;
    private final RefreshTokenRepository refreshTokenRepository;
    private final UserPreferenceRepository userPreferenceRepository;

    @Value("${fileSystemPath}")
    private String FOLDER_PATH;

    @Transactional(readOnly = true)
    public UserInfoResDto getUserInfo(String email) {
        User user = userRepository.findByEmail(email).orElseThrow(()-> new CustomException(ExceptionCode.USER_NOT_EXIST));
        return UserInfoResDto.from(user);
    }

    public UserInfoResDto createUser(SignUpUserReqDto signUpUserReqDto){
        if(userRepository.existsByEmail(signUpUserReqDto.email())){
            throw new CustomException(ExceptionCode.USER_DUPLICATED_EMAIL);
        }

        User user = User.builder()
                .name(signUpUserReqDto.name())
                .email(signUpUserReqDto.email())
                .password(passwordEncoder.encode(signUpUserReqDto.password()))
                .profileFilePath("/image/default.jpg")
                .role("ROLE_USER")
                .build();
        userRepository.save(user);

        // User의 mypage 생성
        MyPage myPage = MyPage.builder()
                .user(user)
                .resumeCompletionPercentage(10)
                .build();
        myPageRepository.save(myPage);

        Resume resume = Resume.builder()
                .email(signUpUserReqDto.email())
                .idPhotoUrl("/image/default.jpg")
                .user(user)
                .build();
        resumeRepository.save(resume);

        List<Experience> experiences = new ArrayList<>();
        for (int i = 0; i < 3; i++) {
            Experience experience = Experience.builder()
                    .resume(resume)
                    .build();
            experiences.add(experience);
        }
        experienceRepository.saveAll(experiences);

        List<Education> educations = new ArrayList<>();
        for (int i = 0; i < 3; i++) {
            Education education = Education.builder()
                    .resume(resume)
                    .build();
            educations.add(education);
        }
        educationRepository.saveAll(educations);

        return UserInfoResDto.from(user);
    }

    public byte[] downloadProfileFromFileSystem(String email) {
        User user = userRepository.findByEmail(email).orElseThrow(()-> new CustomException(ExceptionCode.USER_NOT_EXIST));
        byte[] profileImg= fileComponent.downloadPhotoFromFileSystem(user.getProfileFilePath());
        return profileImg;
    }

    public UserInfoResDto updateProfileImg(String email, MultipartFile updateFile) {
        User user = userRepository.findByEmail(email).orElseThrow(()-> new CustomException(ExceptionCode.USER_NOT_EXIST));
        String updateFileName = FileNameGenerator.generatorName(updateFile.getOriginalFilename());
        String updateFilePath = FOLDER_PATH + updateFileName;
        log.info("새로운 이미지 경로 : {}", updateFilePath);

        fileComponent.updateFileSystemProfileImg(user.getProfileFilePath(), updateFilePath, updateFile);

        user.updateUserProfileUrl(updateFilePath);

        return UserInfoResDto.from(user);
    }

    public SignInResDto signIn(SignInReqDto signInReqDto){
        User user = userRepository.findByEmail(signInReqDto.email()).orElseThrow(() -> new RuntimeException());

        if(!passwordEncoder.matches(signInReqDto.password(),user.getPassword())){
            throw new RuntimeException();
        }

        String accessToken = jwtProvider.createAccessToken(user.getEmail(), user.getRole(), user.getName(),user.getId());
        String refreshToken = jwtProvider.createRefreshToken(user.getEmail(),user.getRole(),user.getName(),user.getId());
        refreshTokenRepository.save(new RefreshToken(user.getId(), refreshToken));
        SignInResDto sign = SignInResDto.of(accessToken,refreshToken);

        return sign;
    }

    public UserInfoResDto updateUserInfo(String email, UpdateUserInfo updateUserInfo) {
        User user = userRepository.findByEmail(email).orElseThrow(()-> new RuntimeException());
        if(updateUserInfo.name() != null){
            user.updateName(updateUserInfo.name());
        }
        return UserInfoResDto.from(user);
    }

    public void deleteUserInfo(String email) {
        User user = userRepository.findByEmail(email).orElseThrow(()-> new RuntimeException());
        UserPreference userPreference = userPreferenceRepository.findByUser(user).orElseThrow(() -> new CustomException(ExceptionCode.USER_PREFERENCE_NOT_EXIST));
        userPreferenceRepository.delete(userPreference);
        userRepository.deleteById(user.getId());
    }

    public SignInResDto reissueAccessToken(HttpServletRequest request){

        String token = jwtProvider.getTokenFromHeader(request);
        log.info("refreshToken : {}",token);
        Long userId = jwtProvider.getUserId(token);
        log.info("userId : {}", userId);

        RefreshToken refreshToken = refreshTokenRepository.findById(userId).orElseThrow(()->new CustomException(ExceptionCode.TOKEN_EXPIRED));
        log.info("refreshTokenId : {}", refreshToken.getId());

        if(!refreshToken.getRefreshToken().equals(token)) {
            throw new CustomException(ExceptionCode.TOKEN_INVALID);
        }

        User user = userRepository.findById(userId).orElseThrow(()-> new CustomException(ExceptionCode.USER_NOT_EXIST));

        String newAccessToken = jwtProvider.createAccessToken(user.getEmail(), user.getRole(), user.getName(),user.getId());
        String newRefreshToken = jwtProvider.createRefreshToken(user.getEmail(), user.getRole(), user.getName(),user.getId());

        SignInResDto signInResDto = SignInResDto.builder()
                .accessToken(newAccessToken)
                .refreshToken(newRefreshToken)
                .build();

        refreshTokenRepository.save(new RefreshToken(userId, newRefreshToken));

        return signInResDto;
    }
}

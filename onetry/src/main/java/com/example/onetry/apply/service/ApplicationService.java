package com.example.onetry.apply.service;

import com.example.onetry.apply.dto.ApplicationInfo;
import com.example.onetry.apply.entity.Application;
import com.example.onetry.apply.entity.Apply;
import com.example.onetry.apply.repository.ApplicationRepository;
import com.example.onetry.apply.repository.ApplyRepository;
import com.example.onetry.exception.CustomException;
import com.example.onetry.exception.ExceptionCode;
import com.example.onetry.mypage.entity.MyPage;
import com.example.onetry.mypage.repository.MyPageRepository;
import com.example.onetry.user.entity.User;
import com.example.onetry.user.repository.UserRepository;
import com.example.onetry.util.NowTimeUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.log4j.Log4j2;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
@Transactional
@Log4j2
public class ApplicationService {
    private final ApplicationRepository applicationRepository;
    private final ApplyRepository applyRepository;
    private final UserRepository userRepository;
    private final MyPageRepository myPageRepository;

    @Transactional(readOnly = true)
    public List<ApplicationInfo> getAllApplications(String email, String sortBy) {
        User user = userRepository.findByEmail(email).orElseThrow(()-> new CustomException(ExceptionCode.USER_NOT_EXIST));
        List<Application> applications;
        if(sortBy.equals("name_asc")){
            applications = applicationRepository.findByUserOrderByCompanyNameAsc(user);
        }else if(sortBy.equals("name_desc")){
            applications = applicationRepository.findByUserOrderByCompanyNameDesc(user);
        }else if(sortBy.equals("recent_asc")){
            applications = applicationRepository.findByUserOrderByCreateDateAsc(user);
        }else if(sortBy.equals("deadline_asc")){
            applications = applicationRepository.findByUserOrderByApplicationDeadLineAsc(user);
        }else if(sortBy.equals("deadline_desc")){
            applications = applicationRepository.findByUserOrderByApplicationDeadLineDesc(user);
        }else{
            applications = applicationRepository.findByUserOrderByCreateDateDesc(user);
        }
        if(applications.size() == 0){
            throw new CustomException(ExceptionCode.APPLICATION_NOT_EXIST);
        }

        log.info("첫번째 조회 결과 : {}", applications.get(0).getCreateDate());
        return applications.stream().map(ApplicationInfo::from).toList();
    }

    public void deleteApplication(String email, Long id) {
        User user = userRepository.findByEmail(email).orElseThrow(()->new CustomException(ExceptionCode.USER_NOT_EXIST));
        Application application = applicationRepository.findById(id).orElseThrow(()->new CustomException(ExceptionCode.APPLICATION_NOT_EXIST));
        Apply apply = applyRepository.findById(application.getApplyId()).orElseThrow(()-> new CustomException(ExceptionCode.APPLY_NOT_EXIST));
        MyPage myPage = myPageRepository.findByUser(user).orElseThrow(() -> new CustomException(ExceptionCode.MY_PAGE_NOT_EXIST));
        if(!user.getId().equals(application.getUser().getId())){
            throw new CustomException(ExceptionCode.APPLICATION_NOT_EXIST);
        }
        applicationRepository.delete(application);
        applyRepository.delete(apply);
        myPage.minusAppliedCompanyCount();
        myPage.updateAppliedCompanyModified(NowTimeUtil.timeNowInZone("Asia/Seoul"));
    }
}

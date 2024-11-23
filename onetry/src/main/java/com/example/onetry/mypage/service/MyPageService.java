package com.example.onetry.mypage.service;

import com.example.onetry.exception.CustomException;
import com.example.onetry.exception.ExceptionCode;
import com.example.onetry.mypage.dto.ComparisonInfo;
import com.example.onetry.mypage.dto.MyPageInfo;
import com.example.onetry.mypage.dto.MyPageStatisticsDto;
import com.example.onetry.mypage.entity.MyPage;
import com.example.onetry.mypage.repository.MyPageRepository;
import com.example.onetry.user.entity.User;
import com.example.onetry.user.repository.UserRepository;
import com.example.onetry.util.TimeAgoCalculator;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Transactional
public class MyPageService {
    private final MyPageRepository myPageRepository;
    private final UserRepository userRepository;
    public MyPageInfo getMyPageInfo(String email) {
        User user = userRepository.findByEmail(email).orElseThrow(()->new CustomException(ExceptionCode.USER_NOT_EXIST));
        MyPage myPage = myPageRepository.findByUser(user).orElseThrow(()->new CustomException(ExceptionCode.MY_PAGE_NOT_EXIST));
        String resumeTimeAgo = TimeAgoCalculator.findTimeAgo(myPage.getLastResumeModified());
        String certificationTimeAgo = TimeAgoCalculator.findTimeAgo(myPage.getLastCertificationModified());
        String appliedTimeAgo = TimeAgoCalculator.findTimeAgo(myPage.getLastAppliedTime());
        String preferenceTimeAgo = TimeAgoCalculator.findTimeAgo(myPage.getLastPreferenceModified());

        return MyPageInfo.of(myPage,resumeTimeAgo, certificationTimeAgo, appliedTimeAgo, preferenceTimeAgo);
    }

    public ComparisonInfo getCompareMyPageInfo(String email) {
        User user = userRepository.findByEmail(email).orElseThrow(()->new CustomException(ExceptionCode.USER_NOT_EXIST));
        MyPage myPage = myPageRepository.findByUser(user).orElseThrow(()->new CustomException(ExceptionCode.MY_PAGE_NOT_EXIST));
        int myPortfolioCount = myPage.getPortfolioCount();
        int myVolunteeringTime = myPage.getVolunteeringTime();
        int myCertificationCount = myPage.getCertificationCount();
        MyPageStatisticsDto avgCount = myPageRepository.findAverageExcludingUser(user.getId());
        int avgPortfolioCount = doubleToInt(avgCount.getPortfolioCount());
        int avgVolunteeringTime = doubleToInt(avgCount.getVolunteeringTime());
        int avgCertificationCount = doubleToInt(avgCount.getCertificationCount());        String portfolioCompare = "포트폴리오 관련 "+compare(myPortfolioCount, avgPortfolioCount);
        String volunteeringCompare= "봉사활동 관련 "+compare(myVolunteeringTime, avgVolunteeringTime);
        String certificationCompare= "자격증 관련 "+compare(myCertificationCount, avgCertificationCount);

        return ComparisonInfo.of(certificationCompare,volunteeringCompare,portfolioCompare,
                avgCertificationCount,avgVolunteeringTime,avgPortfolioCount,
                myCertificationCount,myVolunteeringTime,myPortfolioCount);
    }

    public int doubleToInt(Double averCount){
        return Integer.parseInt(String.valueOf((int) Math.ceil(averCount)));
    }
    private String compare(int my, int avg){
        if(my > avg){
            return "충족";
        }else if(my == avg){
            return "보통";
        }else{
            return "부족";
        }
    }
}

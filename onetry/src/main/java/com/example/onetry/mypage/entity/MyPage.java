package com.example.onetry.mypage.entity;

import com.example.onetry.user.entity.User;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.OnDelete;
import org.hibernate.annotations.OnDeleteAction;

import java.time.LocalDateTime;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "mypage")
public class MyPage {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private int portfolioCount;

    private int volunteeringTime;

    private int resumeCompletionPercentage;
    private LocalDateTime lastResumeModified;

    private int certificationCount;
    private LocalDateTime lastCertificationModified;

    private int appliedCompanyCount;
    private LocalDateTime lastAppliedTime;

    private LocalDateTime lastPreferenceModified;

    @OneToOne
    @JoinColumn(name = "user_id", nullable = false)
    @OnDelete(action = OnDeleteAction.CASCADE)
    private User user;

    @Builder
    protected MyPage(int portfolioCount, int volunteeringTime,
                     int resumeCompletionPercentage, LocalDateTime lastResumeModified,
                     int certificationCount, LocalDateTime lastCertificationModified,
                     int appliedCompanyCount, LocalDateTime lastAppliedTime,
                     LocalDateTime lastPreferenceModified, User user) {
        this.portfolioCount = portfolioCount;
        this.volunteeringTime = volunteeringTime;
        this.resumeCompletionPercentage = resumeCompletionPercentage;
        this.lastResumeModified = lastResumeModified;
        this.certificationCount = certificationCount;
        this.lastCertificationModified = lastCertificationModified;
        this.appliedCompanyCount = appliedCompanyCount;
        this.lastAppliedTime = lastAppliedTime;
        this.lastPreferenceModified = lastPreferenceModified;
        this.user = user;
    }

    public void plusCertificationCount(){
        this.certificationCount = this.certificationCount + 1;
    }

    public void minusCertificationCount(){
        this.certificationCount = this.certificationCount - 1;
    }

    public void plusAppliedCompanyCount(){
        this.appliedCompanyCount = this.appliedCompanyCount + 1;
    }

    public void minusAppliedCompanyCount(){
        this.appliedCompanyCount = this.appliedCompanyCount - 1;
    }
    public void plusPortfolioCount(){
        this.portfolioCount = this.portfolioCount + 1;
    }
    public void minusPortfolioCount(){
        this.portfolioCount = this.portfolioCount - 1;
    }

    public void plusVolunteeringTime(int volunteeringTime){this.volunteeringTime += volunteeringTime;}

    public void minusVolunteeringTime(int volunteeringTime){this.volunteeringTime -= volunteeringTime;}

    public void updateResumeCompletePercentage(int resumeCompletionPercentage){
        this.resumeCompletionPercentage = resumeCompletionPercentage;
    }

    public void updateAppliedCompanyModified(LocalDateTime modifiedTime){
        this.lastCertificationModified = modifiedTime;
    }

    public void updatePreferenceModified(LocalDateTime modifiedTime){
        this.lastPreferenceModified = modifiedTime;
    }
    public void updateCertificationModified(LocalDateTime modifiedTime){
        this.lastCertificationModified = modifiedTime;
    }
    public void updateResumeModified(LocalDateTime modifiedTime){
        this.lastResumeModified = modifiedTime;
    }

}

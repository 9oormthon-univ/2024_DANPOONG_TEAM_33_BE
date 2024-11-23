package com.example.onetry.userpreference.entity;

import com.example.onetry.user.entity.User;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.OnDelete;
import org.hibernate.annotations.OnDeleteAction;

import java.util.ArrayList;
import java.util.List;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "user_prfreference")
@ToString
public class UserPreference {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // 지역 정보
    private String region;
    private String subRegion;

    // 경력 정보
    private String career;

    // 업종 정보
    private String industryCategory; // 예: "기획 - 전략"
    private String subIndustry; // 예: "마케팅"

    // 학력 정보
    private String educationLevel; // 예: "2~3년제", "4년제", "사이버", "고졸"

    // 근무 요일 정보
    @ElementCollection // 별도의 엔티티를 만들 필요 없이 리스트나 컬렉션 데이터를 테이블에 저장 가능
    @CollectionTable(name = "user_work_days", joinColumns = @JoinColumn(name = "user_preference_id"))
    @Column(name = "work_day")
    private List<String> workDays = new ArrayList<>(); // 예: ["월", "화", "수"]

    // 목표 기업 정보
    @ElementCollection
    @CollectionTable(name = "user_target_companies", joinColumns = @JoinColumn(name = "user_preference_id"))
    @Column(name = "company_name")
    private List<String> targetCompanies = new ArrayList<>(); // 예: ["삼성전자", "네이버", "카카오"]

    @OneToOne
    @JoinColumn(name="user_id")
    @OnDelete(action = OnDeleteAction.CASCADE)
    private User user;


    @Builder
    protected UserPreference(String region, String subRegion, String career, String industryCategory,
                             String subIndustry, String educationLevel, List<String> targetCompanies,User user) {
        this.region = region;
        this.subRegion = subRegion;
        this.career = career;
        this.industryCategory = industryCategory;
        this.subIndustry = subIndustry;
        this.educationLevel = educationLevel;
        this.workDays =  List.of("월","화","수","목","금");
        this.targetCompanies = targetCompanies;
        this.user = user;
    }

    public void updateRegion(String region, String subRegion) {
        this.region = region;
        this.subRegion = subRegion;
    }

    public void updateCareer(String career) {
        this.career = career;
    }

    public void updateIndustry(String industryCategory, String subIndustry) {
        this.industryCategory = industryCategory;
        this.subIndustry = subIndustry;
    }

    public void updateEducationLevel(String educationLevel) {
        this.educationLevel = educationLevel;
    }

    public void updateWorkDays(List<String> workDays) {
        if (workDays != null) {
            this.workDays = new ArrayList<>(workDays);
        } else {
            this.workDays.clear(); // 빈 리스트로 초기화
        }
    }

    public void updateTargetCompanies(List<String> targetCompanies) {
        if (targetCompanies != null) {
            this.targetCompanies = new ArrayList<>(targetCompanies);
        } else {
            this.targetCompanies.clear(); // 빈 리스트로 초기화
        }
    }
}

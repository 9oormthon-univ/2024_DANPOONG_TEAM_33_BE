package com.example.onetry.apply.entity;

import com.example.onetry.common.BaseTimeEntity;
import com.example.onetry.user.entity.User;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.OnDelete;
import org.hibernate.annotations.OnDeleteAction;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

@Entity
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Getter
@Table(name = "apply")
public class Apply extends BaseTimeEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private Long companyId;
    private String portfolio;
    private String volunteeringTime;
    private String userGrade;
    private String averageGrade;
    private int applicantCount;
    private LocalDate applicationDeadLine;

    @ElementCollection
    @CollectionTable(name = "additional_certifications", joinColumns = @JoinColumn(name = "apply_id"))
    private List<String> additionalCertification = new ArrayList<>();

    @Enumerated(EnumType.STRING)
    private ApplicationState status;

    @ManyToOne
    @JoinColumn(name = "user_id")
    @OnDelete(action = OnDeleteAction.CASCADE)
    private User user;
    @Builder
    public Apply(Long companyId, String portfolio, String volunteeringTime, String userGrade, String averageGrade,
                 int applicantCount, LocalDate applicationDeadLine, List<String> additionalCertification,
                 ApplicationState status, User user){
        this.companyId = companyId;
        this.portfolio = portfolio;
        this.volunteeringTime = volunteeringTime;
        this.userGrade = userGrade;
        this.averageGrade =averageGrade;
        this.applicantCount = applicantCount;
        this.applicationDeadLine = applicationDeadLine;
        this.additionalCertification = additionalCertification;
        this.status = status;
        this.user = user;
    }
}

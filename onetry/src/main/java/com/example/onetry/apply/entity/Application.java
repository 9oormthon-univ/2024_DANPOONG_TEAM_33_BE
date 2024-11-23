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
@Table(name = "application")
public class Application extends BaseTimeEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private Long applyId;
    private String title;
    private String companyName;

    private LocalDate applicationDeadLine;
    private int applicantCount;

    @ElementCollection()
    @CollectionTable(name = "required_certifications", joinColumns = @JoinColumn(name = "application_id"))
    private List<String> requiredCertifications = new ArrayList<>();

    private String userGrade;
    private String averageGrade;

    @Enumerated(EnumType.STRING)
    private ApplicationState status;

    @ManyToOne
    @JoinColumn(name = "user_id")
    @OnDelete(action = OnDeleteAction.CASCADE)
    private User user;

    @Builder
    protected Application(Long applyId, String title, String companyName, LocalDate applicationDeadLine, int applicantCount,
                          List<String> requiredCertifications, String userGrade, String averageGrade,
                          ApplicationState status, User user){
        this.applyId = applyId;
        this.title = title;
        this.companyName = companyName;
        this.applicantCount = applicantCount;
        this.applicationDeadLine = applicationDeadLine;
        this.requiredCertifications = requiredCertifications;
        this.userGrade = userGrade;
        this.averageGrade = averageGrade;
        this.status = status;
        this.user = user;
    }

}

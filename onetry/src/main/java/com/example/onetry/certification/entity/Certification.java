package com.example.onetry.certification.entity;

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

@Entity
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Getter
@Table(name = "certification")
public class Certification extends BaseTimeEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "certification_name")
    private String certificationName;

    @Column(name = "issuing_organization")
    private String issuingOrganization;

    @Column(name = "acquisition_date")
    private LocalDate acquisitionDate;

    @Column(name = "generateFileName")
    private String generateFileName;

    @Column(name = "certificationPath")
    private String certificationPath;

    @ManyToOne
    @JoinColumn(name = "user_id")
    @OnDelete(action = OnDeleteAction.CASCADE)
    private User user;

    @Builder
    protected Certification(String certificationName, String issuingOrganization, LocalDate acquisitionDate,String generateFileName, String certificationPath, User user){
        this.certificationName = certificationName;
        this.issuingOrganization = issuingOrganization;
        this.acquisitionDate = acquisitionDate;
        this.certificationPath = certificationPath;
        this.generateFileName = generateFileName;
        this.user = user;
    }
}

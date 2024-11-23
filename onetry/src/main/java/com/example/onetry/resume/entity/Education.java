package com.example.onetry.resume.entity;

import com.example.onetry.resume.dto.req.EducationUpdateDto;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.OnDelete;
import org.hibernate.annotations.OnDeleteAction;

@Entity
@Getter
@Setter
@Table(name = "education")
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Education {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String period;
    private String schoolName;
    private String major;
    private String graduationStatus;
    private Double gpa;

    @ManyToOne
    @JoinColumn(name = "resume_id")
    @OnDelete(action = OnDeleteAction.CASCADE)
    private Resume resume;

    @Builder
    private Education(Resume resume) {
        this.resume = resume;
    }

    public void updateFromDto(EducationUpdateDto dto) {
        if (dto.schoolName() != null) this.schoolName = dto.schoolName();
        if (dto.gpa() != null) this.gpa = dto.gpa();
        if (dto.major() != null) this.major = dto.major();
        if (dto.period() != null) this.period = dto.period();
        if (dto.graduationStatus() != null) this.graduationStatus = dto.graduationStatus();
    }
}
